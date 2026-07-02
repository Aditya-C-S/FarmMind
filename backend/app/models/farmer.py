"""
Farmer model for FarmMind backend.
Represents a farmer in the system.
"""

from sqlalchemy import Column, String, DateTime, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class Farmer(Base):
    """
    Farmer ORM model.
    Stores farmer information and maintains relationship with fields.
    """
    
    __tablename__ = "farmers"
    
    # Primary Key
    farmer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Farmer Information
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    district = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Farmer(farmer_id={self.farmer_id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "farmer_id": str(self.farmer_id),
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "district": self.district,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }