"""
Application Configuration
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./recruitment.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = None
    
    # Groq LLM (free tier - get key at https://console.groq.com)
    GROQ_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
