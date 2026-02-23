"""
Applications Routes
Handles job application operations
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.application import ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services.application_service import application_service
from app.services.job_matching import job_matching_service
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply for a job
    """
    # Check if job exists
    job = job_matching_service.get_job_by_id(db, application_data.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    if application_service.has_already_applied(db, current_user.id, application_data.job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create application
    application = application_service.create_application(
        db=db,
        user_id=current_user.id,
        job_id=application_data.job_id,
        cover_letter=application_data.cover_letter,
        resume_url=application_data.resume_url
    )
    
    return application


@router.get("", response_model=List[ApplicationResponse])
async def list_my_applications(
    status: Optional[ApplicationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all applications for the current user
    """
    applications = application_service.get_user_applications(
        db=db,
        user_id=current_user.id,
        status=status
    )
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific application
    """
    application = application_service.get_application_by_id(
        db=db,
        application_id=application_id,
        user_id=current_user.id
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.put("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: int,
    update_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update application status (for recruiters)
    """
    if current_user.role not in [UserRole.RECRUITER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update application status"
        )
    
    application = application_service.update_application_status(
        db=db,
        application_id=application_id,
        status=update_data.status
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
async def list_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all applications for a specific job (for recruiters)
    """
    if current_user.role not in [UserRole.RECRUITER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view job applications"
        )
    
    applications = application_service.get_job_applications(db=db, job_id=job_id)
    return applications
