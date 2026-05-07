from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from services.analytics_service import AnalyticsService

router = APIRouter()

class AnalyticsRequest(BaseModel):
    user_id: str
    period: str = "week"  # day, week, month, all
    metrics: List[str] = ["all"]

class PerformanceMetrics(BaseModel):
    user_id: str
    session_id: str
    overall_score: float
    detailed_scores: Dict[str, float]
    behavior_metrics: Dict[str, float]
    completion_time: int

@router.post("/dashboard")
async def get_dashboard_analytics(request: AnalyticsRequest):
    """Get comprehensive dashboard analytics"""
    try:
        analytics_service = AnalyticsService()
        dashboard_data = await analytics_service.get_dashboard_data(
            user_id=request.user_id,
            period=request.period
        )
        
        return JSONResponse(content={
            "success": True,
            "data": dashboard_data,
            "period": request.period,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard analytics: {str(e)}")

@router.post("/performance-trends")
async def get_performance_trends(request: AnalyticsRequest):
    """Get performance trends over time"""
    try:
        analytics_service = AnalyticsService()
        trends = await analytics_service.get_performance_trends(
            user_id=request.user_id,
            period=request.period
        )
        
        return JSONResponse(content={
            "success": True,
            "trends": trends,
            "period": request.period,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance trends: {str(e)}")

@router.post("/skills-breakdown")
async def get_skills_breakdown(request: AnalyticsRequest):
    """Get detailed skills breakdown"""
    try:
        analytics_service = AnalyticsService()
        skills_data = await analytics_service.get_skills_breakdown(
            user_id=request.user_id,
            period=request.period
        )
        
        return JSONResponse(content={
            "success": True,
            "skills_breakdown": skills_data,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching skills breakdown: {str(e)}")

@router.post("/comparison")
async def get_peer_comparison(request: AnalyticsRequest):
    """Get user performance compared to peers"""
    try:
        analytics_service = AnalyticsService()
        comparison = await analytics_service.get_peer_comparison(
            user_id=request.user_id
        )
        
        return JSONResponse(content={
            "success": True,
            "comparison": comparison,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching peer comparison: {str(e)}")

@router.post("/record-performance")
async def record_performance(metrics: PerformanceMetrics):
    """Record performance metrics for a session"""
    try:
        analytics_service = AnalyticsService()
        result = await analytics_service.record_performance(metrics)
        
        return JSONResponse(content={
            "success": True,
            "recorded": result,
            "recorded_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording performance: {str(e)}")

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, time_period: str = "week"):
    """Get performance leaderboard"""
    try:
        analytics_service = AnalyticsService()
        leaderboard = await analytics_service.get_leaderboard(
            limit=limit,
            time_period=time_period
        )
        
        return JSONResponse(content={
            "success": True,
            "leaderboard": leaderboard,
            "time_period": time_period,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")

@router.get("/user-stats/{user_id}")
async def get_user_statistics(user_id: str):
    """Get comprehensive user statistics"""
    try:
        analytics_service = AnalyticsService()
        stats = await analytics_service.get_user_statistics(user_id)
        
        return JSONResponse(content={
            "success": True,
            "user_id": user_id,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user statistics: {str(e)}")

@router.post("/export-data")
async def export_user_data(request: AnalyticsRequest):
    """Export user performance data"""
    try:
        analytics_service = AnalyticsService()
        export_data = await analytics_service.export_user_data(
            user_id=request.user_id,
            period=request.period
        )
        
        return JSONResponse(content={
            "success": True,
            "export_data": export_data,
            "exported_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.delete("/user-data/{user_id}")
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR compliance)"""
    try:
        analytics_service = AnalyticsService()
        result = await analytics_service.delete_user_data(user_id)
        
        return JSONResponse(content={
            "success": True,
            "deleted": result,
            "deleted_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user data: {str(e)}")
