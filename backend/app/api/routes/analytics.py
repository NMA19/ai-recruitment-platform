"""
Analytics Routes
Provides endpoints for chatbot performance metrics (PFE requirement #7)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User, UserRole
from ...core.security import get_current_active_user
from ...services.ai_service import ai_service


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get chatbot performance analytics summary
    Requires admin or recruiter role
    """
    # Check authorization
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and recruiters can view analytics"
        )
    
    summary = ai_service.get_analytics_summary(days=days)
    return summary


@router.get("/daily")
def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="Number of days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get daily chatbot statistics"""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and recruiters can view analytics"
        )
    
    if ai_service.analytics:
        return ai_service.analytics.get_daily_stats(days=days)
    
    return {"error": "Analytics not available"}


@router.get("/intents")
def get_top_intents(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get most common user intents"""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and recruiters can view analytics"
        )
    
    if ai_service.analytics:
        return ai_service.analytics.get_top_intents(limit=limit)
    
    return []


@router.get("/languages")
def get_language_distribution(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get language usage distribution"""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and recruiters can view analytics"
        )
    
    if ai_service.analytics:
        return ai_service.analytics.get_language_distribution()
    
    return {}


@router.get("/export")
def export_analytics(
    format: str = Query("json", regex="^(json|text)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export analytics report"""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can export analytics"
        )
    
    if ai_service.analytics:
        return {"report": ai_service.analytics.export_metrics(format=format)}
    
    return {"error": "Analytics not available"}


@router.get("/status")
def get_ai_service_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI service status (NLP, ML, LLM availability)"""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and recruiters can view service status"
        )
    
    return ai_service.get_service_status()


@router.post("/feedback")
def submit_feedback(
    interaction_timestamp: str,
    satisfied: bool,
    feedback_text: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit user feedback for a chatbot interaction"""
    if ai_service.analytics:
        ai_service.analytics.record_feedback(
            interaction_timestamp=interaction_timestamp,
            satisfied=satisfied,
            feedback_text=feedback_text
        )
        return {"status": "feedback recorded"}
    
    return {"error": "Analytics not available"}
