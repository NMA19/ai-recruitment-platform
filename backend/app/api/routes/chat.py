"""
Chat Routes
Main chatbot conversation endpoint
This is the CORE FEATURE of the application
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.chat import ChatMessage, ChatResponse, ChatIntent, ConversationResponse
from app.services.ai_service import ai_service
from app.services.job_matching import job_matching_service
from app.services.application_service import application_service
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Main chat endpoint - The heart of the AI recruitment platform
    
    Flow:
    1. Receive user message
    2. Send to AI for intent extraction
    3. Process based on intent
    4. Return intelligent response
    """
    
    # Step 1: AI extracts intent and parameters
    extraction = await ai_service.extract_intent(message.message)
    
    # Step 2: Process based on intent
    context = {"params": extraction.model_dump()}
    jobs = None
    
    if extraction.intent == ChatIntent.SEARCH_JOB:
        # Search for matching jobs
        jobs = job_matching_service.search_from_ai_extraction(db, extraction)
        context["jobs"] = jobs
        
    elif extraction.intent == ChatIntent.APPLY_JOB:
        # Handle job application
        if extraction.job_id:
            # Check if already applied
            if application_service.has_already_applied(db, current_user.id, extraction.job_id):
                context["already_applied"] = True
            else:
                job = job_matching_service.get_job_by_id(db, extraction.job_id)
                if job:
                    application = application_service.create_application(
                        db, current_user.id, extraction.job_id
                    )
                    context["success"] = application is not None
                    context["job"] = job
                    
    elif extraction.intent == ChatIntent.LIST_APPLICATIONS:
        # Get user's applications
        applications = application_service.get_user_applications(db, current_user.id)
        context["applications"] = applications
        
    elif extraction.intent == ChatIntent.GET_JOB_DETAILS:
        # Get specific job details
        if extraction.job_id:
            job = job_matching_service.get_job_by_id(db, extraction.job_id)
            if job:
                jobs = [job]
                context["jobs"] = jobs
    
    # Step 3: Generate response
    response_text = await ai_service.generate_response(extraction.intent, context)
    
    # Step 4: Save conversation to database
    conversation = Conversation(
        user_id=current_user.id,
        message=message.message,
        response=response_text,
        intent=extraction.intent.value,
        extracted_params=json.dumps(extraction.model_dump())
    )
    db.add(conversation)
    db.commit()
    
    # Step 5: Return response
    return ChatResponse(
        message=response_text,
        intent=extraction.intent,
        extracted_data=extraction,
        jobs=[{
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "contract_type": j.contract_type.value if j.contract_type else None,
            "skills": j.skills
        } for j in jobs] if jobs else None
    )


@router.post("/guest", response_model=ChatResponse)
async def chat_guest(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint for non-authenticated users
    Limited functionality - only search and general questions
    """
    
    # AI extracts intent
    extraction = await ai_service.extract_intent(message.message)
    
    context = {"params": extraction.model_dump()}
    jobs = None
    
    # Only allow certain intents for guests
    if extraction.intent == ChatIntent.SEARCH_JOB:
        jobs = job_matching_service.search_from_ai_extraction(db, extraction)
        context["jobs"] = jobs
    elif extraction.intent in [ChatIntent.APPLY_JOB, ChatIntent.LIST_APPLICATIONS]:
        # Require login for these actions
        return ChatResponse(
            message="Please log in or create an account to apply for jobs and track your applications.",
            intent=extraction.intent,
            extracted_data=extraction
        )
    
    response_text = await ai_service.generate_response(extraction.intent, context)
    
    return ChatResponse(
        message=response_text,
        intent=extraction.intent,
        extracted_data=extraction,
        jobs=[{
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "contract_type": j.contract_type.value if j.contract_type else None,
            "skills": j.skills
        } for j in jobs] if jobs else None
    )


@router.get("/history", response_model=list[ConversationResponse])
async def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's chat history
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return conversations
