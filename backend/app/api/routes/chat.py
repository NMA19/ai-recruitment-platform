"""
Chat Routes
Handles AI chatbot interactions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import ChatMessage, User
from ...schemas.schemas import ChatMessage as ChatMessageSchema, ChatResponse, ChatHistoryItem
from ...services.ai_service import ai_service
from ...core.security import get_current_active_user, get_optional_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def send_message(
    chat_message: ChatMessageSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI chatbot (authenticated users)"""
    # Save user message
    user_msg = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=chat_message.message
    )
    db.add(user_msg)
    db.commit()

    # Process message with AI service
    response = ai_service.process_message(
        message=chat_message.message,
        db=db,
        user=current_user
    )

    # Save assistant response
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=response["response"]
    )
    db.add(assistant_msg)
    db.commit()

    return response


@router.post("/guest", response_model=ChatResponse)
def send_message_guest(
    chat_message: ChatMessageSchema,
    db: Session = Depends(get_db)
):
    """Send a message to the AI chatbot (guest users)"""
    # Process message without user context
    response = ai_service.process_message(
        message=chat_message.message,
        db=db,
        user=None
    )

    return response


@router.get("/history", response_model=List[ChatHistoryItem])
def get_chat_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for authenticated user"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    # Reverse to get chronological order
    return list(reversed(messages))
