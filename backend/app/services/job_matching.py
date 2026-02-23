"""
Job Matching Service (Business Logic Layer)
Handles job search, filtering, and recommendation logic

This layer makes your project not just a chatbot - it's the BRAIN.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.job import Job, ContractType
from app.schemas.chat import AIExtraction


class JobMatchingService:
    """
    Job Matching and Recommendation Service
    Implements the business logic for finding relevant jobs
    """
    
    def search_jobs(
        self,
        db: Session,
        role: Optional[str] = None,
        location: Optional[str] = None,
        contract_type: Optional[str] = None,
        skills: Optional[List[str]] = None,
        keywords: Optional[str] = None,
        limit: int = 10
    ) -> List[Job]:
        """
        Search for jobs based on criteria extracted from user message
        
        Args:
            db: Database session
            role: Job role/title to search for
            location: Location preference
            contract_type: Type of contract
            skills: List of required skills
            keywords: General search keywords
            limit: Maximum number of results
            
        Returns:
            List of matching Job objects
        """
        query = db.query(Job).filter(Job.is_active == 1)
        
        filters = []
        
        # Filter by role/title
        if role:
            filters.append(
                or_(
                    func.lower(Job.title).contains(role.lower()),
                    func.lower(Job.description).contains(role.lower())
                )
            )
        
        # Filter by location
        if location:
            filters.append(
                func.lower(Job.location).contains(location.lower())
            )
        
        # Filter by contract type
        if contract_type:
            try:
                ct = ContractType(contract_type.lower())
                filters.append(Job.contract_type == ct)
            except ValueError:
                pass  # Invalid contract type, skip filter
        
        # Filter by skills
        if skills and len(skills) > 0:
            skill_filters = []
            for skill in skills:
                skill_filters.append(
                    func.lower(Job.skills).contains(skill.lower())
                )
            filters.append(or_(*skill_filters))
        
        # Filter by general keywords
        if keywords:
            filters.append(
                or_(
                    func.lower(Job.title).contains(keywords.lower()),
                    func.lower(Job.description).contains(keywords.lower()),
                    func.lower(Job.company).contains(keywords.lower()),
                    func.lower(Job.skills).contains(keywords.lower())
                )
            )
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by most recent
        query = query.order_by(Job.created_at.desc())
        
        return query.limit(limit).all()
    
    def search_from_ai_extraction(
        self,
        db: Session,
        extraction: AIExtraction,
        limit: int = 10
    ) -> List[Job]:
        """
        Search for jobs using AI-extracted parameters
        
        Args:
            db: Database session
            extraction: AIExtraction object with intent and parameters
            limit: Maximum number of results
            
        Returns:
            List of matching Job objects
        """
        return self.search_jobs(
            db=db,
            role=extraction.role,
            location=extraction.location,
            contract_type=extraction.contract_type,
            skills=extraction.skills,
            limit=limit
        )
    
    def get_job_by_id(self, db: Session, job_id: int) -> Optional[Job]:
        """Get a specific job by ID"""
        return db.query(Job).filter(Job.id == job_id, Job.is_active == 1).first()
    
    def get_all_jobs(self, db: Session, skip: int = 0, limit: int = 20) -> List[Job]:
        """Get all active jobs with pagination"""
        return db.query(Job).filter(Job.is_active == 1).offset(skip).limit(limit).all()
    
    def calculate_match_score(self, job: Job, extraction: AIExtraction) -> float:
        """
        Calculate a match score between a job and user requirements
        
        Returns:
            Float between 0 and 1 indicating match quality
        """
        score = 0.0
        max_score = 0.0
        
        # Role match (40% weight)
        if extraction.role:
            max_score += 0.4
            if extraction.role.lower() in job.title.lower():
                score += 0.4
            elif extraction.role.lower() in job.description.lower():
                score += 0.2
        
        # Location match (30% weight)
        if extraction.location:
            max_score += 0.3
            if extraction.location.lower() in job.location.lower():
                score += 0.3
        
        # Contract type match (20% weight)
        if extraction.contract_type:
            max_score += 0.2
            if job.contract_type and job.contract_type.value == extraction.contract_type:
                score += 0.2
        
        # Skills match (10% weight per skill, max 30%)
        if extraction.skills and job.skills:
            job_skills_lower = job.skills.lower()
            skill_matches = sum(1 for s in extraction.skills if s.lower() in job_skills_lower)
            skill_score = min(0.3, skill_matches * 0.1)
            score += skill_score
            max_score += min(0.3, len(extraction.skills) * 0.1)
        
        # Normalize score
        if max_score > 0:
            return score / max_score
        return 0.5  # Default score when no criteria provided
    
    def get_recommended_jobs(
        self,
        db: Session,
        extraction: AIExtraction,
        limit: int = 5
    ) -> List[dict]:
        """
        Get job recommendations with match scores
        
        Returns:
            List of dicts with job and match_score
        """
        jobs = self.search_from_ai_extraction(db, extraction, limit=limit * 2)
        
        # Calculate scores and sort
        scored_jobs = [
            {"job": job, "match_score": self.calculate_match_score(job, extraction)}
            for job in jobs
        ]
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return scored_jobs[:limit]


# Singleton instance
job_matching_service = JobMatchingService()
