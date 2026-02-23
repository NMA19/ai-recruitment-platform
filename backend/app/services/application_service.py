"""
Application Service
Handles job application business logic
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User


class ApplicationService:
    """Service for managing job applications"""
    
    def create_application(
        self,
        db: Session,
        user_id: int,
        job_id: int,
        cover_letter: Optional[str] = None,
        resume_url: Optional[str] = None
    ) -> Optional[Application]:
        """
        Create a new job application
        
        Returns:
            Application object if successful, None if job doesn't exist
        """
        # Check if job exists and is active
        job = db.query(Job).filter(Job.id == job_id, Job.is_active == 1).first()
        if not job:
            return None
        
        # Create application
        application = Application(
            user_id=user_id,
            job_id=job_id,
            cover_letter=cover_letter,
            resume_url=resume_url,
            status=ApplicationStatus.PENDING
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return application
    
    def has_already_applied(self, db: Session, user_id: int, job_id: int) -> bool:
        """Check if user has already applied for this job"""
        existing = db.query(Application).filter(
            Application.user_id == user_id,
            Application.job_id == job_id
        ).first()
        return existing is not None
    
    def get_user_applications(
        self,
        db: Session,
        user_id: int,
        status: Optional[ApplicationStatus] = None
    ) -> List[Application]:
        """Get all applications for a user"""
        query = db.query(Application).filter(Application.user_id == user_id)
        
        if status:
            query = query.filter(Application.status == status)
        
        return query.order_by(Application.created_at.desc()).all()
    
    def get_application_by_id(
        self,
        db: Session,
        application_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Application]:
        """Get a specific application"""
        query = db.query(Application).filter(Application.id == application_id)
        
        if user_id:
            query = query.filter(Application.user_id == user_id)
        
        return query.first()
    
    def update_application_status(
        self,
        db: Session,
        application_id: int,
        status: ApplicationStatus
    ) -> Optional[Application]:
        """Update application status (for recruiters)"""
        application = db.query(Application).filter(Application.id == application_id).first()
        
        if application:
            application.status = status
            db.commit()
            db.refresh(application)
        
        return application
    
    def get_job_applications(
        self,
        db: Session,
        job_id: int
    ) -> List[Application]:
        """Get all applications for a specific job (for recruiters)"""
        return db.query(Application).filter(
            Application.job_id == job_id
        ).order_by(Application.created_at.desc()).all()


# Singleton instance
application_service = ApplicationService()
