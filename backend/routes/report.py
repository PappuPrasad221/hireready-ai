from fastapi import APIRouter, HTTPException
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


class ReportAutomationRequest(BaseModel):
    reportData: Dict[str, Any]
    candidateProfile: Dict[str, Any]
    interviewId: str = ""


class ReportEmailRequest(BaseModel):
    candidateProfile: Dict[str, Any]
    pdfInfo: Dict[str, Any]
    reportId: str = ""


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
        pdf_info = PDFReportService().generate(linked_report_data, payload.candidateProfile)
        email_result = EmailFallbackManager().send_report_email(payload.candidateProfile, pdf_info, report_id)
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
