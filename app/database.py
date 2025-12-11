"""
Database Configuration and Session Management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from app.config import settings

# Load environment variables from .env
load_dotenv()

# Read DB URL from settings (FastAPI config)
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine (PostgreSQL compatible)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # automatically removes dead connections
    future=True               # modern SQLAlchemy engine behavior
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Database session dependency
    Usage in routes: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


