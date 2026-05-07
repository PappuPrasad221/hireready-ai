from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import PyPDF2
import io
import os
from datetime import datetime

from services.resume_analyzer_fixed import ResumeAnalyzer
from services.gemini_service import GeminiService
from utils.file_handler import FileHandler
from firebase_config import get_firestore_db

router = APIRouter()

class TextRequest(BaseModel):
    text: str

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and analyze resume"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        file_handler = FileHandler()
        file_path = await file_handler.save_upload_file(file, "resumes")
        
        # Analyze resume using enhanced AI
        analyzer = ResumeAnalyzer()
        analysis = await analyzer.analyze_resume(file_path)
        
        # Calculate resume score using the analysis
        gemini_service = GeminiService()
        score_response = await gemini_service.evaluate_resume(str(analysis))
        db = get_firestore_db()
        resume_id = file_path.split("/")[-1].rsplit(".", 1)[0]
        if db:
            try:
                db.collection("resumes").document(resume_id).set({
                    "file_path": file_path,
                    "analysis": analysis,
                    "score": score_response.get("score", 75),
                    "uploaded_at": datetime.now().isoformat(),
                })
            except Exception as firestore_error:
                print(f"Firestore resume write skipped: {firestore_error}")
        
        return JSONResponse(content={
            "success": True,
            "resume_id": resume_id,
            "file_path": file_path,
            "analysis": analysis,
            "score": score_response.get("score", 75),
            "feedback": score_response.get("feedback", "Resume uploaded successfully"),
            "uploaded_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.get("/analysis/{resume_id}")
async def get_resume_analysis(resume_id: str):
    """Get previously analyzed resume data"""
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        return JSONResponse(content={
            "resume_id": resume_id,
            "skills": ["React", "Node.js", "Python", "AWS", "Docker"],
            "experience": [
                "Senior Software Engineer at Tech Corp (2021-Present)",
                "Full Stack Developer at StartupXYZ (2019-2021)"
            ],
            "education": [
                "B.S. Computer Science - State University (2014-2018)"
            ],
            "projects": [
                "E-commerce Platform with React & Node.js",
                "AI-powered Chatbot using Python"
            ],
            "score": 78,
            "analyzed_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resume analysis: {str(e)}")

@router.post("/extract-skills")
async def extract_skills_from_text(request: TextRequest):
    """Extract skills from raw text"""
    try:
        analyzer = ResumeAnalyzer()
        skills = await analyzer.extract_skills(request.text)
        
        return JSONResponse(content={
            "success": True,
            "skills": skills
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting skills: {str(e)}")

async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        
        return text_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")
