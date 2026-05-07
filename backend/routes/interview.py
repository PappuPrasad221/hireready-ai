from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Union
from datetime import datetime

from services.question_generator import QuestionGenerator
from services.evaluation_service import EvaluationService
from services.gemini_service import GeminiService
from services.behavior_tracker import BehaviorTracker
from firebase_config import get_firestore_db

router = APIRouter()

class InterviewRequest(BaseModel):
    company: str
    role: str
    location: str
    resume_data: Dict[str, Any]
    job_insights: Dict[str, Any]

class AnswerEvaluation(BaseModel):
    question: Union[str, Dict[str, Any]]
    answer: str
    question_type: str = "general"
    behavior_data: Dict[str, Any]
    resume_context: Dict[str, Any] = {}
    job_insights: Dict[str, Any] = {}

class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    company: str
    role: str
    questions: List[Union[str, Dict[str, Any]]]
    answers: List[Dict[str, Any]]
    behavior_data: List[Dict[str, Any]]
    scores: Dict[str, float]

@router.post("/generate-questions")
async def generate_interview_questions(request: InterviewRequest):
    """Generate personalized interview questions"""
    try:
        generator = QuestionGenerator()
        questions = await generator.generate_questions(
            resume_data=request.resume_data,
            job_insights=request.job_insights,
            role=request.role,
            company=request.company
        )
        
        return JSONResponse(content={
            "success": True,
            "questions": questions,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@router.post("/start")
async def start_interview(request: InterviewRequest):
    """Required API: start interview and return structured rounds."""
    return await start_interview_session(request)

@router.post("/evaluate-answer")
async def evaluate_answer(evaluation: AnswerEvaluation):
    """Evaluate user's answer using AI"""
    try:
        evaluator = EvaluationService()
        result = await evaluator.evaluate_answer(
            question=evaluation.question,
            answer=evaluation.answer,
            question_type=evaluation.question_type,
            behavior_data=evaluation.behavior_data,
            resume_context=evaluation.resume_context,
            job_insights=evaluation.job_insights,
        )
        db = get_firestore_db()
        if db:
            try:
                db.collection("evaluations").add({
                    "evaluation": result,
                    "created_at": datetime.now().isoformat(),
                })
            except Exception as firestore_error:
                print(f"Firestore evaluation write skipped: {firestore_error}")
        
        return JSONResponse(content={
            "success": True,
            "evaluation": result,
            "evaluated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")

@router.post("/evaluate")
async def evaluate_answer_required(evaluation: AnswerEvaluation):
    """Required API alias for answer evaluation."""
    return await evaluate_answer(evaluation)

@router.post("/followup-question")
async def generate_followup_question(evaluation: AnswerEvaluation):
    """Generate follow-up question based on weak answer"""
    try:
        gemini_service = GeminiService()
        followup = await gemini_service.generate_followup_question(
            original_question=evaluation.question,
            answer=evaluation.answer,
            evaluation_score=evaluation.behavior_data.get("score", 0)
        )
        
        return JSONResponse(content={
            "success": True,
            "followup_question": followup,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating follow-up: {str(e)}")

@router.post("/followup")
async def generate_followup_required(evaluation: AnswerEvaluation):
    """Required API alias for follow-up generation."""
    return await generate_followup_question(evaluation)

@router.post("/start-session")
async def start_interview_session(request: InterviewRequest):
    """Start a new interview session"""
    try:
        # Generate questions
        generator = QuestionGenerator()
        questions = await generator.generate_questions(
            resume_data=request.resume_data,
            job_insights=request.job_insights,
            role=request.role,
            company=request.company
        )
        
        # Create session
        session_data = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": "user_123",  # Would come from authentication
            "company": request.company,
            "role": request.role,
            "location": request.location,
            "questions": questions,
            "answers": [],
            "behavior_data": [],
            "scores": {},
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # In a real implementation, save to database
        db = get_firestore_db()
        if db:
            try:
                db.collection("interviews").document(session_data["session_id"]).set(session_data)
            except Exception as firestore_error:
                print(f"Firestore interview write skipped: {firestore_error}")
        
        return JSONResponse(content={
            "success": True,
            "session": session_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

@router.post("/end-session")
async def end_interview_session(session: InterviewSession):
    """End interview session and generate final report"""
    try:
        evaluator = EvaluationService()
        final_report = await evaluator.generate_final_report(session)
        
        return JSONResponse(content={
            "success": True,
            "report": final_report,
            "completed_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_data(session_id: str):
    """Get interview session data"""
    try:
        # In a real implementation, fetch from database
        return JSONResponse(content={
            "session_id": session_id,
            "status": "completed",
            "overall_score": 82,
            "detailed_scores": {
                "technical": 85,
                "communication": 78,
                "confidence": 80,
                "behavior": 88
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")

@router.post("/track-behavior")
async def track_user_behavior(behavior_data: Dict[str, Any]):
    """Track user behavior during interview"""
    try:
        tracker = BehaviorTracker()
        analysis = await tracker.analyze_behavior(behavior_data)
        
        return JSONResponse(content={
            "success": True,
            "behavior_analysis": analysis,
            "tracked_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking behavior: {str(e)}")
