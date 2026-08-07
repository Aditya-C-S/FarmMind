"""
Fertilizer Service module.
Contains business logic for fertilizer application operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import logging

from app.models.fertilizer_application import FertilizerApplication
from app.models.crop import Crop
from app.schemas.fertilizer_application import FertilizerApplicationCreate, FertilizerApplicationUpdate

logger = logging.getLogger(__name__)


class FertilizerService:
    """Service class for fertilizer operations"""
    
    @staticmethod
    def create_fertilizer(db: Session, fertilizer_data: FertilizerApplicationCreate) -> FertilizerApplication:
        """Create a new fertilizer application record"""
        crop = db.query(Crop).filter(Crop.crop_id == fertilizer_data.crop_id).first()
        if not crop:
            raise ValueError(f"Crop with ID {fertilizer_data.crop_id} not found")
        
        try:
            db_fertilizer = FertilizerApplication(
                crop_id=fertilizer_data.crop_id,
                application_date=fertilizer_data.application_date,
                fertilizer_type=fertilizer_data.fertilizer_type,
                nitrogen_kg=fertilizer_data.nitrogen_kg,
                phosphorus_kg=fertilizer_data.phosphorus_kg,
                potassium_kg=fertilizer_data.potassium_kg,
                amount_kg_ha=fertilizer_data.amount_kg_ha,
                amount_total_kg=fertilizer_data.amount_total_kg,
                method=fertilizer_data.method,
                cost=fertilizer_data.cost,
                growth_stage=fertilizer_data.growth_stage,
                brand=fertilizer_data.brand,
                batch_number=fertilizer_data.batch_number,
                weather_conditions=fertilizer_data.weather_conditions,
                notes=fertilizer_data.notes,
            )
            db.add(db_fertilizer)
            db.commit()
            db.refresh(db_fertilizer)
            logger.info(f"✓ Fertilizer record created: {db_fertilizer.fertilizer_id}")
            return db_fertilizer
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating fertilizer record: {str(e)}")
            raise
    
    @staticmethod
    def get_fertilizer_by_id(db: Session, fertilizer_id: UUID) -> FertilizerApplication | None:
        """Get fertilizer by ID"""
        return db.query(FertilizerApplication).filter(FertilizerApplication.fertilizer_id == fertilizer_id).first()
    
    @staticmethod
    def get_fertilizers_by_crop(db: Session, crop_id: UUID, skip: int = 0, limit: int = 100) -> list[FertilizerApplication]:
        """Get all fertilizer applications for a specific crop"""
        return db.query(FertilizerApplication).filter(FertilizerApplication.crop_id == crop_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_fertilizers_by_type(db: Session, crop_id: UUID, fertilizer_type: str) -> list[FertilizerApplication]:
        """Get fertilizer applications by type for a crop"""
        return db.query(FertilizerApplication).filter(
            FertilizerApplication.crop_id == crop_id,
            FertilizerApplication.fertilizer_type == fertilizer_type
        ).all()
    
    @staticmethod
    def get_fertilizers_by_stage(db: Session, crop_id: UUID, growth_stage: str) -> list[FertilizerApplication]:
        """Get fertilizer applications by growth stage"""
        return db.query(FertilizerApplication).filter(
            FertilizerApplication.crop_id == crop_id,
            FertilizerApplication.growth_stage == growth_stage
        ).all()
    
    @staticmethod
    def get_fertilizers_by_date_range(db: Session, crop_id: UUID, start_date: date, end_date: date) -> list[FertilizerApplication]:
        """Get fertilizer applications within date range"""
        return db.query(FertilizerApplication).filter(
            FertilizerApplication.crop_id == crop_id,
            FertilizerApplication.application_date >= start_date,
            FertilizerApplication.application_date <= end_date
        ).all()
    
    @staticmethod
    def get_fertilizer_stats(db: Session, crop_id: UUID) -> dict:
        """Get fertilizer statistics for a crop"""
        fertilizers = db.query(FertilizerApplication).filter(FertilizerApplication.crop_id == crop_id).all()
        
        if not fertilizers:
            return {
                "total_applications": 0,
                "total_nitrogen_kg": 0,
                "total_phosphorus_kg": 0,
                "total_potassium_kg": 0,
                "total_amount_kg": 0,
                "total_cost": 0,
                "average_nitrogen_kg": 0,
                "average_phosphorus_kg": 0,
                "average_potassium_kg": 0,
                "average_cost": 0,
            }
        
        total_nitrogen = sum(f.nitrogen_kg or 0 for f in fertilizers)
        total_phosphorus = sum(f.phosphorus_kg or 0 for f in fertilizers)
        total_potassium = sum(f.potassium_kg or 0 for f in fertilizers)
        total_amount = sum(f.amount_total_kg or 0 for f in fertilizers)
        total_cost = sum(f.cost or 0 for f in fertilizers)
        
        return {
            "total_applications": len(fertilizers),
            "total_nitrogen_kg": total_nitrogen,
            "total_phosphorus_kg": total_phosphorus,
            "total_potassium_kg": total_potassium,
            "total_amount_kg": total_amount,
            "total_cost": total_cost,
            "average_nitrogen_kg": total_nitrogen / len(fertilizers),
            "average_phosphorus_kg": total_phosphorus / len(fertilizers),
            "average_potassium_kg": total_potassium / len(fertilizers),
            "average_cost": total_cost / len(fertilizers),
        }
    
    @staticmethod
    def update_fertilizer(db: Session, fertilizer_id: UUID, fertilizer_data: FertilizerApplicationUpdate) -> FertilizerApplication | None:
        """Update fertilizer record"""
        db_fertilizer = db.query(FertilizerApplication).filter(FertilizerApplication.fertilizer_id == fertilizer_id).first()
        
        if not db_fertilizer:
            return None
        
        try:
            update_data = fertilizer_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_fertilizer, field, value)
            
            db.commit()
            db.refresh(db_fertilizer)
            logger.info(f"✓ Fertilizer updated: {fertilizer_id}")
            return db_fertilizer
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating fertilizer: {str(e)}")
            raise
    
    @staticmethod
    def delete_fertilizer(db: Session, fertilizer_id: UUID) -> bool:
        """Delete fertilizer record"""
        db_fertilizer = db.query(FertilizerApplication).filter(FertilizerApplication.fertilizer_id == fertilizer_id).first()
        
        if not db_fertilizer:
            return False
        
        try:
            db.delete(db_fertilizer)
            db.commit()
            logger.info(f"✓ Fertilizer deleted: {fertilizer_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting fertilizer: {str(e)}")
            raise
    
    @staticmethod
    def count_fertilizers_by_crop(db: Session, crop_id: UUID) -> int:
        """Count fertilizer applications for a crop"""
        return db.query(FertilizerApplication).filter(FertilizerApplication.crop_id == crop_id).count()