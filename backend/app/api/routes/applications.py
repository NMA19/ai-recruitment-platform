"""
Applications Routes
Handles job applications
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import Application, Job, User, UserRole, ApplicationStatus
from ...schemas.schemas import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from ...core.security import get_current_active_user


router = APIRouter(prefix="/apply", tags=["Applications"])


@router.post("", response_model=ApplicationResponse)
def apply_for_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Apply for a job"""
    # Check if job exists and is active
    job = db.query(Job).filter(
        Job.id == application_data.job_id,
        Job.is_active == True
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or no longer available"
        )

    # Check if already applied
    existing = db.query(Application).filter(
        Application.job_id == application_data.job_id,
        Application.candidate_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )

    # Create application
    application = Application(
        job_id=application_data.job_id,
        candidate_id=current_user.id,
        cover_letter=application_data.cover_letter,
        resume_url=application_data.resume_url,
        status=ApplicationStatus.PENDING.value
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get("", response_model=List[ApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's applications"""
    applications = db.query(Application).filter(
        Application.candidate_id == current_user.id
    ).order_by(Application.created_at.desc()).all()

    # Load job details for each application
    result = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        app_dict = {
            "id": app.id,
            "job_id": app.job_id,
            "candidate_id": app.candidate_id,
            "cover_letter": app.cover_letter,
            "resume_url": app.resume_url,
            "status": app.status,
            "created_at": app.created_at,
            "job": job
        }
        result.append(app_dict)

    return result


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific application"""
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Check authorization
    job = db.query(Job).filter(Job.id == application.job_id).first()
    is_owner = application.candidate_id == current_user.id
    is_recruiter = job and job.recruiter_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN.value

    if not (is_owner or is_recruiter or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application"
        )

    return application


@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update application status (recruiters only)"""
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Check authorization - only job recruiter or admin can update
    job = db.query(Job).filter(Job.id == application.job_id).first()
    is_recruiter = job and job.recruiter_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN.value

    if not (is_recruiter or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the job recruiter can update application status"
        )

    # Validate status
    valid_statuses = [s.value for s in ApplicationStatus]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    application.status = status_update.status
    db.commit()
    db.refresh(application)

    return application
