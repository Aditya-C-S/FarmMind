"""
Field model for FarmMind backend.
Represents a farm field belonging to a farmer with Phase 2 relationships.
"""

from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.base import Base


class Field(Base):
    """
    Field ORM model.
    Represents a farm field with location and soil information.
    One Farmer can have many Fields.
    """
    
    __tablename__ = "fields"
    
    # Primary Key
    field_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False)
    
    # Field Information
    field_name = Column(String(100), nullable=False)
    area_acres = Column(Numeric(10, 2), nullable=False)
    soil_type = Column(String(50), nullable=True)
    
    # Location Information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Relationships - Phase 1
    farmer = relationship("Farmer", back_populates="fields")
    crops = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    
    # Relationships - Phase 2: Weather Cache
    weather_cache = relationship("WeatherCache", back_populates="field", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Field(field_id={self.field_id}, field_name='{self.field_name}', farmer_id={self.farmer_id})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "field_id": str(self.field_id),
            "farmer_id": str(self.farmer_id),
            "field_name": self.field_name,
            "area_acres": float(self.area_acres) if self.area_acres else None,
            "soil_type": self.soil_type,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
        }