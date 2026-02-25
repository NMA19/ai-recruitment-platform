"""
AI-Powered Recruitment Platform
FastAPI Backend Application

Features:
- ML-based intent classification (sklearn)
- Local LLM via Ollama
- Cloud LLM via OpenAI
- Candidate auto-ranking
- Performance analytics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import engine, Base
from .api.routes import auth_router, jobs_router, applications_router, chat_router
from .api.routes.profile import router as profile_router
from .api.routes.documents import router as documents_router
from .api.routes.analytics import router as analytics_router
from .api.routes.ranking import router as ranking_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Wassit Online - ANEM Platform",
    description="""
    Plateforme de recrutement avec chatbot IA pour ANEM Algérie
    
    ## Features
    - 🤖 AI Chatbot (NLP + LLM)
    - 📊 ML-based Intent Classification
    - 🏆 Automatic Candidate Ranking
    - 📈 Performance Analytics
    - 🌍 Multilingual (FR/AR/EN)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://127.0.0.1:5173", "http://localhost:3000"],
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
app.include_router(documents_router)
app.include_router(analytics_router)
app.include_router(ranking_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Bienvenue sur Wassit Online - Plateforme ANEM",
        "docs": "/docs",
        "version": "1.0.0",
        "features": [
            "AI Chatbot (NLP + LLM)",
            "ML Intent Classification",
            "Candidate Auto-Ranking",
            "Performance Analytics"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    from .services.ai_service import ai_service
    
    status = ai_service.get_service_status()
    
    return {
        "status": "healthy",
        "ai_services": {
            "nlp": status["nlp"]["spacy_fr"] or status["nlp"]["spacy_en"],
            "ml_classifier": status["ml_classifier"]["trained"] if status["ml_classifier"]["available"] else False,
            "ollama": status["llm"]["ollama"]["available"],
            "openai": status["llm"]["openai"]
        }
    }
