"""
Activity Log model for FarmMind backend.
Tracks all farm activities with flexible metadata.
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class ActivityLog(Base):
    """
    Activity Log ORM model.
    Generic logging for any farm activity.
    Uses JSONB for flexible activity-specific data.
    """
    
    __tablename__ = "activity_logs"
    
    # Primary Key
    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.crop_id", ondelete="CASCADE"), nullable=False)
    
    # Activity Information
    activity_type = Column(String(50), nullable=False)  # "irrigation", "fertilizer", "pesticide", "harvest", etc.
    activity_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    performed_by = Column(String(100), nullable=True)  # Person's name who performed the activity
    
    # Flexible metadata for activity-specific data
    # Examples:
    # {"method": "drip", "quantity_liters": 500} for irrigation
    # {"type": "NPK", "amount_kg": 50} for fertilizer
    # {"pesticide": "Cartap", "dosage": "1kg/ha"} for pesticide
    activity_metadata = Column("metadata", JSONB, nullable=True, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    crop = relationship("Crop", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<ActivityLog(activity_id={self.activity_id}, type='{self.activity_type}', crop_id={self.crop_id})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "activity_id": str(self.activity_id),
            "crop_id": str(self.crop_id),
            "activity_type": self.activity_type,
            "activity_date": self.activity_date.isoformat() if self.activity_date else None,
            "description": self.description,
            "performed_by": self.performed_by,
            "metadata": self.activity_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }