"""
Configuration module for FarmMind backend.
Loads environment variables and provides application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic v2 for validation.
    """
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/farmmind"
    
    # API Configuration
    API_TITLE: str = "FarmMind API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered farm decision optimization and post-harvest loss reduction platform"
    
    # Application Mode
    DEBUG: bool = True
    
    # CORS Configuration (for future frontend)
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global settings instance
settings = Settings()