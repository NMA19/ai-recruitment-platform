"""
Pydantic Schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ============ User Schemas ============

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str
    full_name: str
    role: str = "candidate"


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    # Profile fields
    phone: Optional[str] = None
    wilaya: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    anem_registered: bool = False
    anem_registration_date: Optional[datetime] = None
    anem_renewal_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Profile Schemas ============

class EducationEntry(BaseModel):
    """Schema for education entry"""
    institution: str
    degree: str
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    description: Optional[str] = None


class ExperienceEntry(BaseModel):
    """Schema for experience entry"""
    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False
    description: Optional[str] = None


class LanguageEntry(BaseModel):
    """Schema for language entry"""
    language: str
    level: str  # beginner, intermediate, advanced, native


class ProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    wilaya: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None
    education: Optional[List[EducationEntry]] = None
    experience: Optional[List[ExperienceEntry]] = None
    skills: Optional[str] = None
    languages: Optional[List[LanguageEntry]] = None
    anem_registered: Optional[bool] = None
    anem_registration_date: Optional[datetime] = None
    anem_renewal_date: Optional[datetime] = None


class ProfileResponse(BaseModel):
    """Schema for profile response with parsed JSON fields"""
    id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    wilaya: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None
    education: Optional[List[EducationEntry]] = None
    experience: Optional[List[ExperienceEntry]] = None
    skills: Optional[str] = None
    languages: Optional[List[LanguageEntry]] = None
    anem_registered: bool = False
    anem_registration_date: Optional[datetime] = None
    anem_renewal_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[int] = None


# ============ Job Schemas ============

class JobCreate(BaseModel):
    """Schema for creating a job"""
    title: str
    description: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    contract_type: str = "full-time"
    skills: Optional[str] = None


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    description: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    contract_type: Optional[str] = None
    skills: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    """Schema for job response"""
    id: int
    title: str
    description: str
    company: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    contract_type: str
    skills: Optional[str]
    recruiter_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Application Schemas ============

class ApplicationCreate(BaseModel):
    """Schema for creating an application"""
    job_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status"""
    status: str


class ApplicationResponse(BaseModel):
    """Schema for application response"""
    id: int
    job_id: int
    candidate_id: int
    cover_letter: Optional[str]
    resume_url: Optional[str]
    status: str
    created_at: datetime
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True


# ============ Chat Schemas ============

class ChatMessage(BaseModel):
    """Schema for chat message request"""
    message: str


class ChatHistoryItem(BaseModel):
    """Schema for chat history item"""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str
    jobs: Optional[List[JobResponse]] = None
    action: Optional[str] = None
