"""
Disease Service module.
Contains business logic for disease history operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import logging

from app.models.disease_history import DiseaseHistory
from app.models.crop import Crop
from app.schemas.disease_history import DiseaseHistoryCreate, DiseaseHistoryUpdate

logger = logging.getLogger(__name__)


class DiseaseService:
    """Service class for disease history operations"""
    
    @staticmethod
    def create_disease(db: Session, disease_data: DiseaseHistoryCreate) -> DiseaseHistory:
        """Create a new disease record"""
        crop = db.query(Crop).filter(Crop.crop_id == disease_data.crop_id).first()
        if not crop:
            raise ValueError(f"Crop with ID {disease_data.crop_id} not found")
        
        try:
            db_disease = DiseaseHistory(
                crop_id=disease_data.crop_id,
                disease_name=disease_data.disease_name,
                severity=disease_data.severity,
                confidence=disease_data.confidence,
                detected_date=disease_data.detected_date,
                detected_by=disease_data.detected_by,
                treatment_applied=disease_data.treatment_applied,
                treatment_date=disease_data.treatment_date,
                status=disease_data.status,
                prognosis=disease_data.prognosis,
            )
            db.add(db_disease)
            db.commit()
            db.refresh(db_disease)
            logger.info(f"✓ Disease record created: {db_disease.disease_id}")
            return db_disease
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating disease record: {str(e)}")
            raise
    
    @staticmethod
    def get_disease_by_id(db: Session, disease_id: UUID) -> DiseaseHistory | None:
        """Get disease by ID"""
        return db.query(DiseaseHistory).filter(DiseaseHistory.disease_id == disease_id).first()
    
    @staticmethod
    def get_diseases_by_crop(db: Session, crop_id: UUID, skip: int = 0, limit: int = 100) -> list[DiseaseHistory]:
        """Get all diseases for a specific crop"""
        return db.query(DiseaseHistory).filter(DiseaseHistory.crop_id == crop_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_diseases(db: Session, crop_id: UUID) -> list[DiseaseHistory]:
        """Get active diseases for a crop"""
        return db.query(DiseaseHistory).filter(
            DiseaseHistory.crop_id == crop_id,
            DiseaseHistory.status == "active"
        ).all()
    
    @staticmethod
    def get_diseases_by_severity(db: Session, crop_id: UUID, severity: str) -> list[DiseaseHistory]:
        """Get diseases by severity level"""
        return db.query(DiseaseHistory).filter(
            DiseaseHistory.crop_id == crop_id,
            DiseaseHistory.severity == severity
        ).all()
    
    @staticmethod
    def update_disease(db: Session, disease_id: UUID, disease_data: DiseaseHistoryUpdate) -> DiseaseHistory | None:
        """Update disease record"""
        db_disease = db.query(DiseaseHistory).filter(DiseaseHistory.disease_id == disease_id).first()
        
        if not db_disease:
            return None
        
        try:
            update_data = disease_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_disease, field, value)
            
            db.commit()
            db.refresh(db_disease)
            logger.info(f"✓ Disease updated: {disease_id}")
            return db_disease
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating disease: {str(e)}")
            raise
    
    @staticmethod
    def delete_disease(db: Session, disease_id: UUID) -> bool:
        """Delete disease record"""
        db_disease = db.query(DiseaseHistory).filter(DiseaseHistory.disease_id == disease_id).first()
        
        if not db_disease:
            return False
        
        try:
            db.delete(db_disease)
            db.commit()
            logger.info(f"✓ Disease deleted: {disease_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting disease: {str(e)}")
            raise
    
    @staticmethod
    def count_diseases_by_crop(db: Session, crop_id: UUID, status: str | None = None) -> int:
        """Count diseases for a crop"""
        query = db.query(DiseaseHistory).filter(DiseaseHistory.crop_id == crop_id)
        if status:
            query = query.filter(DiseaseHistory.status == status)
        return query.count()