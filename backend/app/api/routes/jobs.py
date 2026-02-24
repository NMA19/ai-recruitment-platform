"""
Jobs Routes
Handles job listing, creation, update, and deletion
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import Job, User, UserRole
from ...schemas.schemas import JobCreate, JobUpdate, JobResponse
from ...core.security import get_current_active_user, get_optional_current_user


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobResponse])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location: Optional[str] = None,
    contract_type: Optional[str] = None,
    skills: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all active jobs with optional filters"""
    query = db.query(Job).filter(Job.is_active == True)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if contract_type:
        query = query.filter(Job.contract_type == contract_type)
    
    if skills:
        query = query.filter(Job.skills.ilike(f"%{skills}%"))
    
    if search:
        query = query.filter(
            (Job.title.ilike(f"%{search}%")) |
            (Job.description.ilike(f"%{search}%")) |
            (Job.company.ilike(f"%{search}%"))
        )

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.post("", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (recruiters and admins only)"""
    if current_user.role not in [UserRole.RECRUITER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create job postings"
        )

    job = Job(
        title=job_data.title,
        description=job_data.description,
        company=job_data.company,
        location=job_data.location,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        contract_type=job_data.contract_type,
        skills=job_data.skills,
        recruiter_id=current_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a job posting (owner or admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check ownership
    if job.recruiter_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job"
        )

    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting (owner or admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check ownership
    if job.recruiter_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}
