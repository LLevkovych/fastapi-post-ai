import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # JWT authentication settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI API keys for content moderation and auto-reply
    GOOGLE_AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis configuration for background tasks
    REDIS_URL: str = "redis://localhost:6379"
    
    # Content moderation settings
    MODERATION_ENABLED: bool = True
    AUTO_BLOCK_ENABLED: bool = True
    
    # Auto-reply settings
    AUTO_REPLY_ENABLED: bool = True
    DEFAULT_AUTO_REPLY_DELAY: int = 60  # seconds
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # CORS settings for frontend integration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Application settings
    APP_NAME: str = "FastPostAI"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()