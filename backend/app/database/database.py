"""
Database module for FarmMind backend.
Creates and manages SQLAlchemy engine and connection pool.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with connection pooling
try:
    engine = create_engine(
        settings.DATABASE_URL,
        # Connection pool settings
        poolclass=QueuePool,
        pool_size=10,  # Number of connections to keep in the pool
        max_overflow=20,  # Maximum overflow connections beyond pool_size
        pool_pre_ping=True,  # Test connection before using (checks if connection is alive)
        pool_recycle=3600,  # Recycle connections after 1 hour
        # Query performance
        echo=settings.DEBUG,  # Log all SQL queries when DEBUG=True
        echo_pool=settings.DEBUG,  # Log connection pool events
        future=True,  # Use SQLAlchemy 2.0 API
    )
    logger.info("✓ Database engine created successfully")
except SQLAlchemyError as e:
    logger.error(f"✗ Failed to create database engine: {str(e)}")
    raise


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Event listener to set connection parameters.
    Useful for PostgreSQL-specific settings if needed in future.
    """
    pass


def get_engine():
    """
    Get the database engine instance.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine


def test_connection():
    """
    Test if database connection works.
    Call this during application startup to verify database connectivity.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✓ Database connection test successful")
            return True
    except SQLAlchemyError as e:
        logger.error(f"✗ Database connection test failed: {str(e)}")
        return False