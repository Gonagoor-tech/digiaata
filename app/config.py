"""
Application Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./digi_aata.db"
    
    # JWT Settings
    SECRET_KEY: str = "digi-aata"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Application
    APP_NAME: str = "DIGI AATA E-Commerce API"
    DEBUG: bool = True
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "./uploads"
    
    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
