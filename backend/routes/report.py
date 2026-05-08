import os
import re

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Any, Dict

from routes.interview import InterviewSession
from services.evaluation_service import EvaluationService
from services.email.email_fallback_manager import EmailFallbackManager
from services.pdf_report_service import PDFReportService
from firebase_config import get_firestore_db
from pydantic import BaseModel

router = APIRouter()


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip()) or "recording"


class ReportAutomationRequest(BaseModel):
    reportData: Dict[str, Any]
    candidateProfile: Dict[str, Any]
    interviewId: str = ""


class ReportEmailRequest(BaseModel):
    candidateProfile: Dict[str, Any]
    pdfInfo: Dict[str, Any]
    reportId: str = ""


@router.post("/recording/upload")
async def upload_interview_recording(
    file: UploadFile = File(...),
    userId: str = Form("anonymous"),
    interviewId: str = Form("interview"),
    candidateName: str = Form("Candidate"),
    recordingFileName: str = Form("recording.webm"),
):
    """Upload an interview recording fallback when Firebase Storage is unavailable."""
    try:
        safe_user_id = _safe_name(userId)
        safe_interview_id = _safe_name(interviewId)
        safe_candidate = _safe_name(candidateName)
        safe_filename = _safe_name(recordingFileName.rsplit(".", 1)[0]) + ".webm"
        if safe_filename == "recording.webm":
            safe_filename = f"HireReady_Interview_Recording_{safe_candidate}_{safe_interview_id}.webm"

        output_dir = os.path.join("uploads", "recordings", safe_user_id, safe_interview_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, safe_filename)

        content = await file.read()
        with open(output_path, "wb") as handle:
            handle.write(content)

        recording_url = f"/uploads/recordings/{safe_user_id}/{safe_interview_id}/{safe_filename}"
        return JSONResponse(content={
            "success": True,
            "recording": {
                "recordingStatus": "uploaded",
                "recordingUrl": recording_url,
                "recordingFileName": safe_filename,
                "recordingMimeType": file.content_type or "video/webm",
                "recordingSize": len(content),
                "recordingUploadedAt": datetime.now().isoformat(),
                "recordingAttachmentMode": "attached" if len(content) <= 10 * 1024 * 1024 else "link",
                "recordingStorage": "backend_fallback",
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading recording: {str(e)}")


@router.post("/generate")
async def generate_report(session: InterviewSession):
    """Generate a final learning-focused interview report."""
    try:
        evaluator = EvaluationService()
        report = await evaluator.generate_final_report(session)
        db = get_firestore_db()
        if db:
            try:
                db.collection("reports").document(report.get("session_id") or "latest").set(report)
            except Exception as firestore_error:
                print(f"Firestore report write skipped: {firestore_error}")
        return JSONResponse(content={
            "success": True,
            "report": report,
            "generated_at": datetime.now().isoformat(),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.post("/generate-pdf")
async def generate_report_pdf(payload: ReportAutomationRequest):
    """Generate a local PDF version of a final interview report."""
    try:
        pdf_info = PDFReportService().generate(payload.reportData, payload.candidateProfile)
        return JSONResponse(content={
            "success": True,
            "pdf": pdf_info,
            "generated_at": datetime.now().isoformat(),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")


@router.post("/email")
async def email_report(payload: ReportEmailRequest):
    """Send an existing PDF report by email using Brevo with Resend fallback."""
    try:
        result = EmailFallbackManager().send_report_email(
            payload.candidateProfile,
            payload.pdfInfo,
            payload.reportId,
        )
        return JSONResponse(content={"success": result.get("emailStatus") != "failed", **result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error emailing report: {str(e)}")


@router.post("/complete")
async def complete_report_automation(payload: ReportAutomationRequest):
    """Generate a PDF report, email it, and persist delivery status."""
    try:
        session_id = payload.candidateProfile.get("sessionId") or payload.reportData.get("sessionId") or payload.reportData.get("session_id", "")
        report_id = payload.reportData.get("reportId") or payload.interviewId or session_id or f"report_{int(datetime.now().timestamp())}"
        linked_report_data = {
            **payload.reportData,
            "userId": payload.candidateProfile.get("userId", ""),
            "candidateName": payload.candidateProfile.get("fullName", ""),
            "candidateEmail": payload.candidateProfile.get("email", ""),
            "sessionId": session_id,
            "interviewId": payload.interviewId or payload.reportData.get("interviewId", "") or payload.reportData.get("session_id", ""),
        }
        recording_info = linked_report_data.get("recording") or {}
        pdf_info = PDFReportService().generate(linked_report_data, payload.candidateProfile)
        email_result = EmailFallbackManager().send_report_email(payload.candidateProfile, pdf_info, report_id, recording_info)
        print(f"Report linked to candidateEmail: {payload.candidateProfile.get('email', '')}")

        report_record = {
            "reportId": report_id,
            "userId": payload.candidateProfile.get("userId", ""),
            "candidateName": payload.candidateProfile.get("fullName", ""),
            "candidateEmail": payload.candidateProfile.get("email", ""),
            "sessionId": session_id,
            "email": payload.candidateProfile.get("email", ""),
            "interviewId": payload.interviewId or payload.reportData.get("session_id", ""),
            "reportData": linked_report_data,
            "pdfUrl": pdf_info.get("pdfUrl", ""),
            "emailStatus": email_result.get("emailStatus", "failed"),
            "emailProvider": email_result.get("emailProvider", ""),
            "emailError": email_result.get("emailError", ""),
            "emailMessageId": email_result.get("emailMessageId", ""),
            "recordingStatus": recording_info.get("recordingStatus", "not_available"),
            "recordingUrl": recording_info.get("recordingUrl", ""),
            "recordingFileName": recording_info.get("recordingFileName", ""),
            "recordingMimeType": recording_info.get("recordingMimeType", ""),
            "recordingSize": recording_info.get("recordingSize", 0),
            "recordingUploadedAt": recording_info.get("recordingUploadedAt", ""),
            "recordingAttachmentMode": email_result.get("recordingAttachmentMode", recording_info.get("recordingAttachmentMode", "not_available")),
            "recordingError": recording_info.get("recordingError", ""),
            "createdAt": datetime.now().isoformat(),
        }

        db = get_firestore_db()
        if db:
            try:
                db.collection("reports").document(report_id).set(report_record)
            except Exception as firestore_error:
                print(f"Firestore automated report write skipped: {firestore_error}")

        return JSONResponse(content={
            "success": True,
            "reportId": report_id,
            "pdf": pdf_info,
            **email_result,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing report automation: {str(e)}")
