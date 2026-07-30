"""
Irrigation model for FarmMind backend.
Tracks all water management operations.
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, DateTime, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.database.base import Base


class Irrigation(Base):
    """
    Irrigation ORM model.
    Tracks all water management operations and costs.
    """
    
    __tablename__ = "irrigation"
    
    # Primary Key
    irrigation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.crop_id", ondelete="CASCADE"), nullable=False)
    
    # Irrigation Information
    irrigation_date = Column(Date, nullable=False)
    
    # Method of irrigation
    method = Column(String(50), nullable=False)  # "drip", "flood", "sprinkler", "manual", "canal", etc.
    
    # Water Quantity
    quantity_liters = Column(Numeric(12, 2), nullable=False)  # Total water used
    
    # Duration
    duration_hours = Column(Numeric(5, 2), nullable=True)  # How long irrigation ran
    
    # Cost Information
    cost = Column(Numeric(10, 2), nullable=True, default=0)  # Cost in ₹
    cost_per_liter = Column(Numeric(8, 4), nullable=True)  # Calculated cost per liter
    
    # Additional Information
    water_source = Column(String(50), nullable=True)  # "borewell", "canal", "tank", "groundwater", etc.
    pressure_level = Column(String(20), nullable=True)  # "low", "medium", "high" (for drip systems)
    
    # Notes
    notes = Column(Text, nullable=True)  # Any additional notes
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    crop = relationship("Crop", back_populates="irrigations")
    
    def __repr__(self) -> str:
        return f"<Irrigation(irrigation_id={self.irrigation_id}, method='{self.method}', qty={self.quantity_liters}L)>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "irrigation_id": str(self.irrigation_id),
            "crop_id": str(self.crop_id),
            "irrigation_date": self.irrigation_date.isoformat() if self.irrigation_date else None,
            "method": self.method,
            "quantity_liters": float(self.quantity_liters) if self.quantity_liters else None,
            "duration_hours": float(self.duration_hours) if self.duration_hours else None,
            "cost": float(self.cost) if self.cost else None,
            "cost_per_liter": float(self.cost_per_liter) if self.cost_per_liter else None,
            "water_source": self.water_source,
            "pressure_level": self.pressure_level,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }