"""
AI-Powered Recruitment Platform
Main FastAPI Application Entry Point

Architecture: Layered Microservice-Oriented Architecture 
integrating an AI service for natural language understanding.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, jobs, applications
from app.core.config import settings
from app.db.database import engine
from app.models import user, job, application, conversation

# Create database tables
user.Base.metadata.create_all(bind=engine)
job.Base.metadata.create_all(bind=engine)
application.Base.metadata.create_all(bind=engine)
conversation.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Recruitment Platform",
    description="An AI-powered recruitment platform with chatbot interface",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/apply", tags=["Applications"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Recruitment Platform",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
