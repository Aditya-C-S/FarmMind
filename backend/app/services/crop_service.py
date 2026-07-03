"""
Crop service module.
Contains business logic for crop CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import logging

from app.models.crop import Crop
from app.models.field import Field
from app.schemas.crop import CropCreate, CropUpdate

logger = logging.getLogger(__name__)


class CropService:
    """Service class for crop-related business logic"""
    
    @staticmethod
    def create_crop(db: Session, crop_data: CropCreate) -> Crop:
        """
        Create a new crop.
        
        Args:
            db: Database session
            crop_data: CropCreate schema with crop details
            
        Returns:
            Crop: Created crop object
            
        Raises:
            ValueError: If field doesn't exist or validation fails
        """
        # Verify field exists
        field = db.query(Field).filter(Field.field_id == crop_data.field_id).first()
        if not field:
            raise ValueError(f"Field with ID {crop_data.field_id} not found")
        
        # Validate dates
        if crop_data.expected_harvest_date <= crop_data.sowing_date:
            raise ValueError("Expected harvest date must be after sowing date")
        
        try:
            db_crop = Crop(
                field_id=crop_data.field_id,
                crop_type=crop_data.crop_type,
                variety=crop_data.variety,
                sowing_date=crop_data.sowing_date,
                expected_harvest_date=crop_data.expected_harvest_date,
                status="active",
            )
            db.add(db_crop)
            db.commit()
            db.refresh(db_crop)
            logger.info(f"✓ Crop created: {db_crop.crop_id}")
            return db_crop
            
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating crop: {str(e)}")
            raise
    
    
    @staticmethod
    def get_crop_by_id(db: Session, crop_id: UUID) -> Crop | None:
        """
        Get a crop by ID.
        
        Args:
            db: Database session
            crop_id: UUID of the crop
            
        Returns:
            Crop: Crop object or None if not found
        """
        return db.query(Crop).filter(Crop.crop_id == crop_id).first()
    
    
    @staticmethod
    def get_all_crops(db: Session, skip: int = 0, limit: int = 100) -> list[Crop]:
        """
        Get all crops with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Crop]: List of crop objects
        """
        return db.query(Crop).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_crops_by_field(db: Session, field_id: UUID, skip: int = 0, limit: int = 100) -> list[Crop]:
        """
        Get all crops grown in a specific field.
        
        Args:
            db: Database session
            field_id: UUID of the field
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Crop]: List of crop objects
        """
        return db.query(Crop).filter(Crop.field_id == field_id).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_crops_by_farmer(db: Session, farmer_id: UUID, skip: int = 0, limit: int = 100) -> list[Crop]:
        """
        Get all crops owned by a specific farmer (through their fields).
        
        Args:
            db: Database session
            farmer_id: UUID of the farmer
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Crop]: List of crop objects
        """
        return db.query(Crop).join(Field).filter(Field.farmer_id == farmer_id).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_crops_by_type(db: Session, crop_type: str, skip: int = 0, limit: int = 100) -> list[Crop]:
        """
        Get all crops of a specific type.
        
        Args:
            db: Database session
            crop_type: Type of crop (e.g., "Rice", "Tomato")
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Crop]: List of crop objects
        """
        return db.query(Crop).filter(Crop.crop_type == crop_type).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def update_crop(db: Session, crop_id: UUID, crop_data: CropUpdate) -> Crop | None:
        """
        Update an existing crop.
        
        Args:
            db: Database session
            crop_id: UUID of the crop to update
            crop_data: CropUpdate schema with updated fields
            
        Returns:
            Crop: Updated crop object or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        db_crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        
        if not db_crop:
            return None
        
        try:
            # Update only provided fields
            update_data = crop_data.model_dump(exclude_unset=True)
            
            # Validate dates if both provided
            if 'sowing_date' in update_data and 'expected_harvest_date' in update_data:
                if update_data['expected_harvest_date'] <= update_data['sowing_date']:
                    raise ValueError("Expected harvest date must be after sowing date")
            
            for field, value in update_data.items():
                setattr(db_crop, field, value)
            
            db.commit()
            db.refresh(db_crop)
            logger.info(f"✓ Crop updated: {crop_id}")
            return db_crop
            
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating crop: {str(e)}")
            raise
    
    
    @staticmethod
    def delete_crop(db: Session, crop_id: UUID) -> bool:
        """
        Delete a crop.
        
        Args:
            db: Database session
            crop_id: UUID of the crop to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        
        if not db_crop:
            return False
        
        try:
            db.delete(db_crop)
            db.commit()
            logger.info(f"✓ Crop deleted: {crop_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting crop: {str(e)}")
            raise
    
    
    @staticmethod
    def count_crops(db: Session, field_id: UUID | None = None, farmer_id: UUID | None = None) -> int:
        """
        Get total count of crops.
        
        Args:
            db: Database session
            field_id: Optional - count crops in specific field
            farmer_id: Optional - count crops owned by farmer
            
        Returns:
            int: Total number of crops
        """
        query = db.query(Crop)
        
        if field_id:
            query = query.filter(Crop.field_id == field_id)
        elif farmer_id:
            query = query.join(Field).filter(Field.farmer_id == farmer_id)
        
        return query.count()