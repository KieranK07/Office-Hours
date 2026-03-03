"""
Configuration settings for the Office Hours API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_TITLE: str = "Office Hours Triage API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Secure FastAPI server for managing student office hours queues"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"  # CHANGE IN PRODUCTION
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Database (SQLite for persistence, optional)
    DATABASE_URL: Optional[str] = None  # Set to "sqlite:///./office_hours.db" for persistence
    
    # System Configuration
    MAX_SEVERITY: int = 5
    MIN_SEVERITY: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
