from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from routes.interview import InterviewSession
from services.evaluation_service import EvaluationService
from firebase_config import get_firestore_db

router = APIRouter()


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
