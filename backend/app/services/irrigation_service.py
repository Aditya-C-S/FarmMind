"""
Irrigation Service module.
Contains business logic for irrigation management operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import logging

from app.models.irrigation import Irrigation
from app.models.crop import Crop
from app.schemas.irrigation import IrrigationCreate, IrrigationUpdate

logger = logging.getLogger(__name__)


class IrrigationService:
    """Service class for irrigation operations"""
    
    @staticmethod
    def create_irrigation(db: Session, irrigation_data: IrrigationCreate) -> Irrigation:
        """Create a new irrigation record"""
        crop = db.query(Crop).filter(Crop.crop_id == irrigation_data.crop_id).first()
        if not crop:
            raise ValueError(f"Crop with ID {irrigation_data.crop_id} not found")
        
        try:
            db_irrigation = Irrigation(
                crop_id=irrigation_data.crop_id,
                irrigation_date=irrigation_data.irrigation_date,
                method=irrigation_data.method,
                quantity_liters=irrigation_data.quantity_liters,
                duration_hours=irrigation_data.duration_hours,
                cost=irrigation_data.cost,
                water_source=irrigation_data.water_source,
                pressure_level=irrigation_data.pressure_level,
                notes=irrigation_data.notes,
            )
            db.add(db_irrigation)
            db.commit()
            db.refresh(db_irrigation)
            logger.info(f"✓ Irrigation record created: {db_irrigation.irrigation_id}")
            return db_irrigation
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating irrigation record: {str(e)}")
            raise
    
    @staticmethod
    def get_irrigation_by_id(db: Session, irrigation_id: UUID) -> Irrigation | None:
        """Get irrigation by ID"""
        return db.query(Irrigation).filter(Irrigation.irrigation_id == irrigation_id).first()
    
    @staticmethod
    def get_irrigations_by_crop(db: Session, crop_id: UUID, skip: int = 0, limit: int = 100) -> list[Irrigation]:
        """Get all irrigations for a specific crop"""
        return db.query(Irrigation).filter(Irrigation.crop_id == crop_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_irrigations_by_method(db: Session, crop_id: UUID, method: str) -> list[Irrigation]:
        """Get irrigations by method for a crop"""
        return db.query(Irrigation).filter(
            Irrigation.crop_id == crop_id,
            Irrigation.method == method
        ).all()
    
    @staticmethod
    def get_irrigations_by_date_range(db: Session, crop_id: UUID, start_date: date, end_date: date) -> list[Irrigation]:
        """Get irrigations within date range"""
        return db.query(Irrigation).filter(
            Irrigation.crop_id == crop_id,
            Irrigation.irrigation_date >= start_date,
            Irrigation.irrigation_date <= end_date
        ).all()
    
    @staticmethod
    def get_irrigation_stats(db: Session, crop_id: UUID) -> dict:
        """Get irrigation statistics for a crop"""
        irrigations = db.query(Irrigation).filter(Irrigation.crop_id == crop_id).all()
        
        if not irrigations:
            return {
                "total_irrigations": 0,
                "total_quantity_liters": 0,
                "total_duration_hours": 0,
                "total_cost": 0,
                "average_quantity_liters": 0,
                "average_duration_hours": 0,
                "average_cost": 0,
            }
        
        total_quantity = sum(i.quantity_liters or 0 for i in irrigations)
        total_duration = sum(i.duration_hours or 0 for i in irrigations)
        total_cost = sum(i.cost or 0 for i in irrigations)
        
        return {
            "total_irrigations": len(irrigations),
            "total_quantity_liters": total_quantity,
            "total_duration_hours": total_duration,
            "total_cost": total_cost,
            "average_quantity_liters": total_quantity / len(irrigations),
            "average_duration_hours": total_duration / len(irrigations),
            "average_cost": total_cost / len(irrigations),
        }
    
    @staticmethod
    def update_irrigation(db: Session, irrigation_id: UUID, irrigation_data: IrrigationUpdate) -> Irrigation | None:
        """Update irrigation record"""
        db_irrigation = db.query(Irrigation).filter(Irrigation.irrigation_id == irrigation_id).first()
        
        if not db_irrigation:
            return None
        
        try:
            update_data = irrigation_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_irrigation, field, value)
            
            db.commit()
            db.refresh(db_irrigation)
            logger.info(f"✓ Irrigation updated: {irrigation_id}")
            return db_irrigation
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating irrigation: {str(e)}")
            raise
    
    @staticmethod
    def delete_irrigation(db: Session, irrigation_id: UUID) -> bool:
        """Delete irrigation record"""
        db_irrigation = db.query(Irrigation).filter(Irrigation.irrigation_id == irrigation_id).first()
        
        if not db_irrigation:
            return False
        
        try:
            db.delete(db_irrigation)
            db.commit()
            logger.info(f"✓ Irrigation deleted: {irrigation_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting irrigation: {str(e)}")
            raise
    
    @staticmethod
    def count_irrigations_by_crop(db: Session, crop_id: UUID) -> int:
        """Count irrigations for a crop"""
        return db.query(Irrigation).filter(Irrigation.crop_id == crop_id).count()