"""
Disease History model for FarmMind backend.
Tracks disease detection, severity, and treatment.
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class DiseaseHistory(Base):
    """
    Disease History ORM model.
    Tracks disease detection, severity, and progression.
    Links to treatment and outcomes.
    """
    
    __tablename__ = "disease_history"
    
    # Primary Key
    disease_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    # Foreign Key
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.crop_id", ondelete="CASCADE"), nullable=False)
    
    # Disease Information
    disease_name = Column(String(100), nullable=False)  # "Leaf Blast", "Stem Borer", "Early Blight", etc.
    severity = Column(String(20), nullable=False)  # "low", "medium", "high"
    
    # Confidence from detection model (0-100)
    # 0-25: low confidence
    # 26-75: medium confidence
    # 76-100: high confidence
    confidence = Column(Numeric(5, 2), nullable=False, default=0)
    
    # Detection and Status
    detected_date = Column(Date, nullable=False)
    detected_by = Column(String(50), nullable=False)  # "user_input", "cv_model", "agonomist"
    
    # Treatment Information
    treatment_applied = Column(Text, nullable=True)  # Pesticide/fungicide name and dosage
    treatment_date = Column(Date, nullable=True)
    
    # Current Status
    status = Column(String(20), nullable=False, default="active")  # "active", "treated", "resolved", "worsened"
    
    # Prognosis
    prognosis = Column(Text, nullable=True)  # Expected progression or outcome
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    crop = relationship("Crop", back_populates="disease_history")
    
    def __repr__(self) -> str:
        return f"<DiseaseHistory(disease_id={self.disease_id}, disease='{self.disease_name}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "disease_id": str(self.disease_id),
            "crop_id": str(self.crop_id),
            "disease_name": self.disease_name,
            "severity": self.severity,
            "confidence": float(self.confidence) if self.confidence else None,
            "detected_date": self.detected_date.isoformat() if self.detected_date else None,
            "detected_by": self.detected_by,
            "treatment_applied": self.treatment_applied,
            "treatment_date": self.treatment_date.isoformat() if self.treatment_date else None,
            "status": self.status,
            "prognosis": self.prognosis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }