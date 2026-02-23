"""
Job Schemas
Pydantic models for job data validation
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContractType(str, Enum):
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    skills: Optional[str] = None
    contract_type: ContractType = ContractType.FULL_TIME
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[str] = None
    contract_type: Optional[ContractType] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    is_active: Optional[int] = None


class JobResponse(JobBase):
    id: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobSearchParams(BaseModel):
    """Parameters extracted by AI for job search"""
    role: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[ContractType] = None
    skills: Optional[List[str]] = None
    keywords: Optional[str] = None
