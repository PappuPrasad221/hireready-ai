from datetime import datetime
import re
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from firebase_config import get_firestore_db

router = APIRouter()


class CandidateProfile(BaseModel):
    fullName: str
    email: str
    phone: str = ""
    institution: str = ""
    branch: str = ""
    targetRole: str = ""

    @field_validator("fullName")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name is required")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", cleaned):
            raise ValueError("A valid email is required")
        return cleaned


@router.post("/profile")
async def save_candidate_profile(profile: CandidateProfile):
    """Save a lightweight candidate profile for report delivery."""
    try:
        user_id = f"user_{uuid4().hex}"
        session_id = f"session_{uuid4().hex}"
        payload = {
            "userId": user_id,
            "sessionId": session_id,
            "fullName": profile.fullName,
            "email": profile.email,
            "phone": profile.phone.strip(),
            "institution": profile.institution.strip(),
            "branch": profile.branch.strip(),
            "targetRole": profile.targetRole.strip(),
            "createdAt": datetime.now().isoformat(),
        }

        db = get_firestore_db()
        if db:
            try:
                db.collection("users").document(user_id).set(payload)
                print("New candidate profile saved")
                print(f"Current userId: {user_id}")
                print(f"Current candidateEmail: {profile.email}")
            except Exception as firestore_error:
                print(f"Firestore user write skipped: {firestore_error}")

        return JSONResponse(content={"success": True, "profile": payload})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")
