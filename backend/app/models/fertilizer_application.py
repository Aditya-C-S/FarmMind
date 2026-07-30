"""
Fertilizer Application model for FarmMind backend.
Tracks all nutrient and fertilizer applications.
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class FertilizerApplication(Base):
    """
    Fertilizer Application ORM model.
    Tracks all fertilizer and nutrient applications.
    Supports cost tracking and ROI calculations.
    """
    
    __tablename__ = "fertilizer_application"
    
    # Primary Key
    fertilizer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.crop_id", ondelete="CASCADE"), nullable=False)
    
    # Application Information
    application_date = Column(Date, nullable=False)
    
    # Fertilizer Type
    # Examples: "NPK 10:26:26", "Urea", "DAP", "Potash", "Neem Coated Urea (NCU)", "Biofertilizer", "Vermicompost"
    fertilizer_type = Column(String(100), nullable=False)
    
    # Nutrient Breakdown (optional - for NPK and complex fertilizers)
    nitrogen_kg = Column(Numeric(8, 2), nullable=True)  # N percentage/amount
    phosphorus_kg = Column(Numeric(8, 2), nullable=True)  # P percentage/amount
    potassium_kg = Column(Numeric(8, 2), nullable=True)  # K percentage/amount
    
    # Application Details
    amount_kg_ha = Column(Numeric(10, 2), nullable=False)  # Amount applied per hectare
    amount_total_kg = Column(Numeric(12, 2), nullable=True)  # Total amount for entire crop
    
    # Application Method
    method = Column(String(50), nullable=False)  # "broadcast", "fertigation", "foliar", "soil_application"
    
    # Cost Information
    cost = Column(Numeric(10, 2), nullable=True, default=0)  # Total cost in ₹
    cost_per_kg = Column(Numeric(8, 2), nullable=True)  # Cost per kg
    
    # Stage Information
    growth_stage = Column(String(50), nullable=True)  # "nursery", "tillering", "flowering", "grain_fill", etc.
    
    # Additional Information
    brand = Column(String(100), nullable=True)  # Brand/manufacturer
    batch_number = Column(String(50), nullable=True)  # Batch number for quality tracking
    weather_conditions = Column(String(100), nullable=True)  # Weather at time of application
    
    # Notes
    notes = Column(Text, nullable=True)  # Any additional notes
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    crop = relationship("Crop", back_populates="fertilizers")
    
    def __repr__(self) -> str:
        return f"<FertilizerApplication(fertilizer_id={self.fertilizer_id}, type='{self.fertilizer_type}', amount={self.amount_kg_ha}kg/ha)>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "fertilizer_id": str(self.fertilizer_id),
            "crop_id": str(self.crop_id),
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "fertilizer_type": self.fertilizer_type,
            "nitrogen_kg": float(self.nitrogen_kg) if self.nitrogen_kg else None,
            "phosphorus_kg": float(self.phosphorus_kg) if self.phosphorus_kg else None,
            "potassium_kg": float(self.potassium_kg) if self.potassium_kg else None,
            "amount_kg_ha": float(self.amount_kg_ha) if self.amount_kg_ha else None,
            "amount_total_kg": float(self.amount_total_kg) if self.amount_total_kg else None,
            "method": self.method,
            "cost": float(self.cost) if self.cost else None,
            "cost_per_kg": float(self.cost_per_kg) if self.cost_per_kg else None,
            "growth_stage": self.growth_stage,
            "brand": self.brand,
            "batch_number": self.batch_number,
            "weather_conditions": self.weather_conditions,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }