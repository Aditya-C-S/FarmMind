"""
Crop model for FarmMind backend.
Represents a crop grown in a field.
"""

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.base import Base


class Crop(Base):
    """
    Crop ORM model.
    Represents a crop grown in a specific field.
    One Field can have many Crops (over time or simultaneously).
    """
    
    __tablename__ = "crops"
    
    # Primary Key
    crop_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.field_id", ondelete="CASCADE"), nullable=False)
    
    # Crop Information
    crop_type = Column(String(50), nullable=False)  # e.g., "Rice", "Tomato"
    variety = Column(String(100), nullable=True)  # e.g., "IR-64", "Arka Samrat"
    
    # Crop Timeline
    sowing_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=False)
    
    # Crop Status
    status = Column(String(20), default="active", nullable=False)  # active, completed, failed
    
    # Relationships
    field = relationship("Field", back_populates="crops")
    
    def __repr__(self) -> str:
        return f"<Crop(crop_id={self.crop_id}, crop_type='{self.crop_type}', field_id={self.field_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "crop_id": str(self.crop_id),
            "field_id": str(self.field_id),
            "crop_type": self.crop_type,
            "variety": self.variety,
            "sowing_date": self.sowing_date.isoformat() if self.sowing_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "status": self.status,
        }