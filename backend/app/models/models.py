"""
SQLAlchemy Database Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ContractType(str, enum.Enum):
    """Contract type enumeration"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"
    FREELANCE = "freelance"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CANDIDATE.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile/CV fields
    phone = Column(String(20), nullable=True)
    wilaya = Column(String(100), nullable=True)  # Algerian province
    address = Column(String(500), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    bio = Column(Text, nullable=True)  # Short summary
    
    # Education & Experience (JSON stored as text)
    education = Column(Text, nullable=True)  # JSON array of education entries
    experience = Column(Text, nullable=True)  # JSON array of experience entries
    skills = Column(Text, nullable=True)  # Comma-separated skills
    languages = Column(Text, nullable=True)  # JSON array of languages with levels
    
    # ANEM specific
    anem_registered = Column(Boolean, default=False)
    anem_registration_date = Column(DateTime, nullable=True)
    anem_renewal_date = Column(DateTime, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False, index=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    contract_type = Column(String(50), default=ContractType.FULL_TIME.value)
    skills = Column(Text, nullable=True)  # Comma-separated skills
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    """Job application model"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)
    status = Column(String(50), default=ApplicationStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")


class ChatMessage(Base):
    """Chat message model for AI conversation history"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for guest
    session_id = Column(String(255), nullable=True)  # For guest sessions
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
