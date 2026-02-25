"""
Candidate Ranking Routes
ML-based candidate ranking for recruiters (PFE requirement #4)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...db.database import get_db
from ...models.models import User, UserRole, Job, Application
from ...core.security import get_current_active_user
from ...services.candidate_ranking import ranking_service


router = APIRouter(prefix="/ranking", tags=["Candidate Ranking"])


class RankedCandidate(BaseModel):
    """Ranked candidate response model"""
    id: int
    full_name: str
    email: str
    skills: Optional[str]
    wilaya: Optional[str]
    ranking_score: float
    score_breakdown: dict
    application_id: int
    applied_at: str


class RankingResponse(BaseModel):
    """Ranking response model"""
    job_id: int
    job_title: str
    total_candidates: int
    candidates: List[dict]


@router.get("/job/{job_id}", response_model=RankingResponse)
def get_ranked_candidates(
    job_id: int,
    top_n: Optional[int] = Query(None, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get ML-ranked candidates for a job posting
    Only accessible by the job's recruiter or admin
    """
    # Get the job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check authorization
    if current_user.role != UserRole.ADMIN.value and job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view rankings for your own job postings"
        )
    
    # Get applications for this job
    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()
    
    if not applications:
        return RankingResponse(
            job_id=job_id,
            job_title=job.title,
            total_candidates=0,
            candidates=[]
        )
    
    # Get candidate profiles
    candidates = []
    for app in applications:
        candidate = db.query(User).filter(User.id == app.candidate_id).first()
        if candidate:
            candidates.append({
                "id": candidate.id,
                "full_name": candidate.full_name,
                "email": candidate.email,
                "skills": candidate.skills,
                "education": candidate.education,
                "experience": candidate.experience,
                "wilaya": candidate.wilaya,
                "application_id": app.id,
                "applied_at": app.created_at.isoformat() if app.created_at else None,
                "cover_letter": app.cover_letter
            })
    
    # Prepare job dict for ranking
    job_dict = {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "skills": job.skills,
        "location": job.location,
        "contract_type": job.contract_type
    }
    
    # Rank candidates
    ranked = ranking_service.rank_candidates(
        job=job_dict,
        candidates=candidates,
        top_n=top_n
    )
    
    return RankingResponse(
        job_id=job_id,
        job_title=job.title,
        total_candidates=len(ranked),
        candidates=ranked
    )


@router.get("/job/{job_id}/explain/{candidate_id}")
def get_ranking_explanation(
    job_id: int,
    candidate_id: int,
    lang: str = Query("fr", regex="^(fr|en|ar)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation for a candidate's ranking
    """
    # Get job and verify access
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if current_user.role != UserRole.ADMIN.value and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get candidate
    candidate = db.query(User).filter(User.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if candidate applied
    application = db.query(Application).filter(
        Application.job_id == job_id,
        Application.candidate_id == candidate_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Candidate has not applied for this job")
    
    # Prepare data for ranking
    job_dict = {
        "title": job.title,
        "description": job.description,
        "skills": job.skills,
        "location": job.location
    }
    
    candidate_dict = {
        "skills": candidate.skills,
        "education": candidate.education,
        "experience": candidate.experience,
        "wilaya": candidate.wilaya,
        "applied_at": application.created_at.isoformat() if application.created_at else None
    }
    
    # Get ranking with breakdown
    ranked = ranking_service.rank_candidates(job_dict, [candidate_dict])
    
    if not ranked:
        raise HTTPException(status_code=500, detail="Could not calculate ranking")
    
    score_breakdown = ranked[0].get("score_breakdown", {})
    
    # Get explanation
    explanation = ranking_service.get_ranking_explanation(score_breakdown)
    
    # Get improvement suggestions
    suggestions = ranking_service.suggest_improvements(job_dict, candidate_dict, lang)
    
    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate.full_name,
        "job_id": job_id,
        "job_title": job.title,
        "ranking_score": ranked[0].get("ranking_score", 0),
        "score_breakdown": score_breakdown,
        "explanation": explanation.get(lang, explanation.get("fr")),
        "improvement_suggestions": suggestions
    }


@router.get("/my-jobs")
def get_my_jobs_with_rankings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all recruiter's job postings with candidate counts
    """
    if current_user.role not in [UserRole.ADMIN.value, UserRole.RECRUITER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access this endpoint"
        )
    
    # Get recruiter's jobs
    if current_user.role == UserRole.ADMIN.value:
        jobs = db.query(Job).filter(Job.is_active == True).all()
    else:
        jobs = db.query(Job).filter(
            Job.recruiter_id == current_user.id,
            Job.is_active == True
        ).all()
    
    result = []
    for job in jobs:
        # Count applications
        app_count = db.query(Application).filter(
            Application.job_id == job.id
        ).count()
        
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "application_count": app_count,
            "has_candidates": app_count > 0
        })
    
    return result


@router.post("/configure-weights")
def configure_ranking_weights(
    skills_match: float = Query(0.35, ge=0, le=1),
    experience_match: float = Query(0.25, ge=0, le=1),
    education_match: float = Query(0.20, ge=0, le=1),
    location_match: float = Query(0.10, ge=0, le=1),
    recency: float = Query(0.10, ge=0, le=1),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Configure ranking weights (admin only)
    Weights should sum to 1.0
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can configure ranking weights"
        )
    
    total = skills_match + experience_match + education_match + location_match + recency
    if abs(total - 1.0) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weights must sum to 1.0 (current sum: {total})"
        )
    
    # Update weights
    from ...services.candidate_ranking import RankingWeights
    ranking_service.weights = RankingWeights(
        skills_match=skills_match,
        experience_match=experience_match,
        education_match=education_match,
        location_match=location_match,
        recency=recency
    )
    
    return {
        "status": "weights updated",
        "weights": {
            "skills_match": skills_match,
            "experience_match": experience_match,
            "education_match": education_match,
            "location_match": location_match,
            "recency": recency
        }
    }
