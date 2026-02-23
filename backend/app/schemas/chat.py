"""
Chat Schemas
Pydantic models for chatbot interactions
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ChatIntent(str, Enum):
    """Possible intents detected from user messages"""
    SEARCH_JOB = "search_job"
    APPLY_JOB = "apply_job"
    GET_JOB_DETAILS = "get_job_details"
    LIST_APPLICATIONS = "list_applications"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


class ChatMessage(BaseModel):
    """User's chat message"""
    message: str


class AIExtraction(BaseModel):
    """Structured data extracted by AI from user message"""
    intent: ChatIntent
    role: Optional[str] = None
    location: Optional[str] = None
    contract_type: Optional[str] = None
    skills: Optional[List[str]] = None
    company: Optional[str] = None
    job_id: Optional[int] = None
    confidence: float = 0.0


class ChatResponse(BaseModel):
    """Response to user's chat message"""
    message: str
    intent: ChatIntent
    extracted_data: Optional[AIExtraction] = None
    jobs: Optional[List[Any]] = None
    additional_info: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Stored conversation record"""
    id: int
    message: str
    response: str
    intent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
