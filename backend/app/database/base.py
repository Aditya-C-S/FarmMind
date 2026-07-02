"""
Database base model module for FarmMind backend.
Provides the declarative base class for SQLAlchemy models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides common configuration and metadata.
    """
    pass