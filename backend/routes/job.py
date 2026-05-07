from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

from services.job_insights_service import JobInsightsService
from services.gemini_service import GeminiService

router = APIRouter()

class JobRequest(BaseModel):
    company: str
    role: str
    location: str

class JobSearchRequest(BaseModel):
    query: str
    location: str
    limit: int = 10

@router.post("/insights")
async def get_job_insights(request: JobRequest):
    """Get comprehensive job insights for a specific role and company"""
    try:
        insights_service = JobInsightsService()
        insights = await insights_service.get_job_insights(
            company=request.company,
            role=request.role,
            location=request.location
        )
        
        return JSONResponse(content={
            "success": True,
            "insights": insights,
            "fetched_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job insights: {str(e)}")

@router.post("/search")
async def search_jobs(request: JobSearchRequest):
    """Search for jobs using The Muse API or similar"""
    try:
        insights_service = JobInsightsService()
        jobs = await insights_service.search_jobs(
            query=request.query,
            location=request.location,
            limit=request.limit
        )
        
        return JSONResponse(content={
            "success": True,
            "jobs": jobs,
            "total": len(jobs),
            "searched_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@router.get("/popular-roles")
async def get_popular_roles():
    """Get list of popular job roles"""
    try:
        popular_roles = [
            "Software Engineer",
            "Product Manager",
            "Data Scientist",
            "UX Designer",
            "DevOps Engineer",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "Machine Learning Engineer",
            "Cloud Architect",
            "Cybersecurity Analyst",
            "Mobile Developer"
        ]
        
        return JSONResponse(content={
            "success": True,
            "popular_roles": popular_roles
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular roles: {str(e)}")

@router.get("/popular-companies")
async def get_popular_companies():
    """Get list of popular tech companies"""
    try:
        popular_companies = [
            "Google",
            "Microsoft",
            "Amazon",
            "Apple",
            "Meta",
            "Netflix",
            "Tesla",
            "Spotify",
            "Uber",
            "Airbnb",
            "LinkedIn",
            "Twitter",
            "Adobe",
            "Salesforce",
            "Oracle"
        ]
        
        return JSONResponse(content={
            "success": True,
            "popular_companies": popular_companies
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular companies: {str(e)}")

@router.get("/skills-for-role/{role}")
async def get_skills_for_role(role: str):
    """Get required skills for a specific role"""
    try:
        skills_map = {
            "Software Engineer": ["JavaScript", "Python", "React", "Node.js", "Git", "SQL", "AWS"],
            "Product Manager": ["Product Strategy", "Data Analysis", "User Research", "Agile", "Communication"],
            "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "TensorFlow", "Data Visualization"],
            "UX Designer": ["Figma", "Adobe XD", "User Research", "Prototyping", "Design Systems"],
            "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Monitoring"],
            "Frontend Developer": ["React", "Vue.js", "TypeScript", "CSS", "HTML", "JavaScript"],
            "Backend Developer": ["Node.js", "Python", "Java", "APIs", "Databases", "Microservices"],
            "Full Stack Developer": ["React", "Node.js", "Python", "SQL", "AWS", "Docker"]
        }
        
        skills = skills_map.get(role, ["JavaScript", "Python", "React", "Node.js", "SQL"])
        
        return JSONResponse(content={
            "success": True,
            "role": role,
            "skills": skills
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching skills: {str(e)}")

@router.post("/salary-estimate")
async def get_salary_estimate(request: JobRequest):
    """Get salary estimate for a role and location"""
    try:
        # Mock salary data - in production, integrate with salary API
        salary_ranges = {
            "Software Engineer": {"entry": 70000, "mid": 120000, "senior": 180000},
            "Product Manager": {"entry": 80000, "mid": 140000, "senior": 200000},
            "Data Scientist": {"entry": 85000, "mid": 130000, "senior": 190000},
            "UX Designer": {"entry": 65000, "mid": 110000, "senior": 160000},
            "DevOps Engineer": {"entry": 90000, "mid": 140000, "senior": 200000}
        }
        
        base_range = salary_ranges.get(request.role, {"entry": 60000, "mid": 100000, "senior": 150000})
        
        # Location multiplier
        location_multipliers = {
            "San Francisco": 1.4,
            "New York": 1.3,
            "Seattle": 1.2,
            "Austin": 1.1,
            "Remote": 1.0
        }
        
        multiplier = location_multipliers.get(request.location, 1.0)
        
        adjusted_range = {
            "entry": int(base_range["entry"] * multiplier),
            "mid": int(base_range["mid"] * multiplier),
            "senior": int(base_range["senior"] * multiplier)
        }
        
        return JSONResponse(content={
            "success": True,
            "salary_range": adjusted_range,
            "location": request.location,
            "role": request.role
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating salary: {str(e)}")
