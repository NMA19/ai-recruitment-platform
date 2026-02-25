"""
AI-Powered Recruitment Platform
FastAPI Backend Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import engine, Base
from .api.routes import auth_router, jobs_router, applications_router, chat_router
from .api.routes.profile import router as profile_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Wassit Online - ANEM Platform",
    description="Plateforme de recrutement avec chatbot IA pour ANEM Algérie",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(chat_router)
app.include_router(profile_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Bienvenue sur Wassit Online - Plateforme ANEM",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
