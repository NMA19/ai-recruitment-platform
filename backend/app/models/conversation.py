"""
Conversation Model
Stores chat history between user and AI chatbot
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)  # User's message
    response = Column(Text, nullable=False)  # AI's response
    intent = Column(String(50), nullable=True)  # Detected intent
    extracted_params = Column(Text, nullable=True)  # JSON string of extracted parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation {self.id} User:{self.user_id}>"
