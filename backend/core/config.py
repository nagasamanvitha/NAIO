from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./naio.db")
    
    # OpenRouter API configuration
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    
    # Groq API configuration (optional)
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY", None)
    
    # Redis configuration (optional)
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()
