"""
Field service module.
Contains business logic for field CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import logging

from app.models.field import Field
from app.models.farmer import Farmer
from app.schemas.field import FieldCreate, FieldUpdate

logger = logging.getLogger(__name__)


class FieldService:
    """Service class for field-related business logic"""
    
    @staticmethod
    def create_field(db: Session, field_data: FieldCreate) -> Field:
        """
        Create a new field.
        
        Args:
            db: Database session
            field_data: FieldCreate schema with field details
            
        Returns:
            Field: Created field object
            
        Raises:
            ValueError: If farmer doesn't exist
        """
        # Verify farmer exists
        farmer = db.query(Farmer).filter(Farmer.farmer_id == field_data.farmer_id).first()
        if not farmer:
            raise ValueError(f"Farmer with ID {field_data.farmer_id} not found")
        
        try:
            db_field = Field(
                farmer_id=field_data.farmer_id,
                field_name=field_data.field_name,
                area_acres=field_data.area_acres,
                soil_type=field_data.soil_type,
                latitude=field_data.latitude,
                longitude=field_data.longitude,
            )
            db.add(db_field)
            db.commit()
            db.refresh(db_field)
            logger.info(f"✓ Field created: {db_field.field_id}")
            return db_field
            
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating field: {str(e)}")
            raise
    
    
    @staticmethod
    def get_field_by_id(db: Session, field_id: UUID) -> Field | None:
        """
        Get a field by ID.
        
        Args:
            db: Database session
            field_id: UUID of the field
            
        Returns:
            Field: Field object or None if not found
        """
        return db.query(Field).filter(Field.field_id == field_id).first()
    
    
    @staticmethod
    def get_all_fields(db: Session, skip: int = 0, limit: int = 100) -> list[Field]:
        """
        Get all fields with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Field]: List of field objects
        """
        return db.query(Field).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_fields_by_farmer(db: Session, farmer_id: UUID, skip: int = 0, limit: int = 100) -> list[Field]:
        """
        Get all fields owned by a specific farmer.
        
        Args:
            db: Database session
            farmer_id: UUID of the farmer
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Field]: List of field objects
        """
        return db.query(Field).filter(Field.farmer_id == farmer_id).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def update_field(db: Session, field_id: UUID, field_data: FieldUpdate) -> Field | None:
        """
        Update an existing field.
        
        Args:
            db: Database session
            field_id: UUID of the field to update
            field_data: FieldUpdate schema with updated fields
            
        Returns:
            Field: Updated field object or None if not found
        """
        db_field = db.query(Field).filter(Field.field_id == field_id).first()
        
        if not db_field:
            return None
        
        try:
            # Update only provided fields
            update_data = field_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_field, field, value)
            
            db.commit()
            db.refresh(db_field)
            logger.info(f"✓ Field updated: {field_id}")
            return db_field
            
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating field: {str(e)}")
            raise
    
    
    @staticmethod
    def delete_field(db: Session, field_id: UUID) -> bool:
        """
        Delete a field.
        
        Args:
            db: Database session
            field_id: UUID of the field to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_field = db.query(Field).filter(Field.field_id == field_id).first()
        
        if not db_field:
            return False
        
        try:
            db.delete(db_field)
            db.commit()
            logger.info(f"✓ Field deleted: {field_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting field: {str(e)}")
            raise
    
    
    @staticmethod
    def count_fields(db: Session, farmer_id: UUID | None = None) -> int:
        """
        Get total count of fields.
        
        Args:
            db: Database session
            farmer_id: Optional - count fields for specific farmer
            
        Returns:
            int: Total number of fields
        """
        query = db.query(Field)
        if farmer_id:
            query = query.filter(Field.farmer_id == farmer_id)
        return query.count()