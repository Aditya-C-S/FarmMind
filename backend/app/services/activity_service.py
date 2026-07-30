"""
Activity Service module.
Contains business logic for activity log operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import logging

from app.models.activity_log import ActivityLog
from app.models.crop import Crop
from app.schemas.activity_log import ActivityLogCreate, ActivityLogUpdate

logger = logging.getLogger(__name__)


class ActivityService:
    """Service class for activity log operations"""
    
    @staticmethod
    def create_activity(db: Session, activity_data: ActivityLogCreate) -> ActivityLog:
        """Create a new activity log entry"""
        crop = db.query(Crop).filter(Crop.crop_id == activity_data.crop_id).first()
        if not crop:
            raise ValueError(f"Crop with ID {activity_data.crop_id} not found")
        
        try:
            db_activity = ActivityLog(
                crop_id=activity_data.crop_id,
                activity_type=activity_data.activity_type,
                activity_date=activity_data.activity_date,
                description=activity_data.description,
                performed_by=activity_data.performed_by,
                metadata=activity_data.metadata,
            )
            db.add(db_activity)
            db.commit()
            db.refresh(db_activity)
            logger.info(f"✓ Activity logged: {db_activity.activity_id}")
            return db_activity
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating activity: {str(e)}")
            raise
    
    @staticmethod
    def get_activity_by_id(db: Session, activity_id: UUID) -> ActivityLog | None:
        """Get activity by ID"""
        return db.query(ActivityLog).filter(ActivityLog.activity_id == activity_id).first()
    
    @staticmethod
    def get_activities_by_crop(db: Session, crop_id: UUID, skip: int = 0, limit: int = 100) -> list[ActivityLog]:
        """Get all activities for a specific crop"""
        return db.query(ActivityLog).filter(ActivityLog.crop_id == crop_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_activities_by_type(db: Session, crop_id: UUID, activity_type: str) -> list[ActivityLog]:
        """Get activities by type for a crop"""
        return db.query(ActivityLog).filter(
            ActivityLog.crop_id == crop_id,
            ActivityLog.activity_type == activity_type
        ).all()
    
    @staticmethod
    def get_activities_by_date_range(db: Session, crop_id: UUID, start_date: date, end_date: date) -> list[ActivityLog]:
        """Get activities within date range"""
        return db.query(ActivityLog).filter(
            ActivityLog.crop_id == crop_id,
            ActivityLog.activity_date >= start_date,
            ActivityLog.activity_date <= end_date
        ).all()
    
    @staticmethod
    def update_activity(db: Session, activity_id: UUID, activity_data: ActivityLogUpdate) -> ActivityLog | None:
        """Update activity record"""
        db_activity = db.query(ActivityLog).filter(ActivityLog.activity_id == activity_id).first()
        
        if not db_activity:
            return None
        
        try:
            update_data = activity_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_activity, field, value)
            
            db.commit()
            db.refresh(db_activity)
            logger.info(f"✓ Activity updated: {activity_id}")
            return db_activity
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating activity: {str(e)}")
            raise
    
    @staticmethod
    def delete_activity(db: Session, activity_id: UUID) -> bool:
        """Delete activity record"""
        db_activity = db.query(ActivityLog).filter(ActivityLog.activity_id == activity_id).first()
        
        if not db_activity:
            return False
        
        try:
            db.delete(db_activity)
            db.commit()
            logger.info(f"✓ Activity deleted: {activity_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting activity: {str(e)}")
            raise
    
    @staticmethod
    def count_activities_by_crop(db: Session, crop_id: UUID) -> int:
        """Count activities for a crop"""
        return db.query(ActivityLog).filter(ActivityLog.crop_id == crop_id).count()