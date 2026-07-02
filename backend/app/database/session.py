"""
Database session module for FarmMind backend.
Provides session management and FastAPI dependency injection.
"""

from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from contextlib import contextmanager
import logging

from app.database.database import engine

# Configure logging
logger = logging.getLogger(__name__)

# Create SessionLocal factory
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit (useful for returning objects in API)
    autoflush=False,  # Don't auto-flush (explicit control)
    autocommit=False,  # Require explicit commit
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection function for FastAPI.
    Provides a database session for each request.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage in route:
        @router.get("/farmers")
        def get_farmers(db: Session = Depends(get_db)):
            return db.query(Farmer).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for getting a database session outside of FastAPI routes.
    Useful for background tasks, scripts, or non-HTTP code.
    
    Usage:
        with get_db_context() as db:
            farmers = db.query(Farmer).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()