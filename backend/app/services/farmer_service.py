"""
Farmer service module.
Contains business logic for farmer CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import logging

from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate, FarmerUpdate

logger = logging.getLogger(__name__)


class FarmerService:
    """Service class for farmer-related business logic"""
    
    @staticmethod
    def create_farmer(db: Session, farmer_data: FarmerCreate) -> Farmer:
        """
        Create a new farmer.
        
        Args:
            db: Database session
            farmer_data: FarmerCreate schema with farmer details
            
        Returns:
            Farmer: Created farmer object
            
        Raises:
            ValueError: If email already exists
        """
        try:
            db_farmer = Farmer(
                name=farmer_data.name,
                phone=farmer_data.phone,
                email=farmer_data.email,
                district=farmer_data.district,
                state=farmer_data.state,
            )
            db.add(db_farmer)
            db.commit()
            db.refresh(db_farmer)
            logger.info(f"✓ Farmer created: {db_farmer.farmer_id}")
            return db_farmer
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"✗ Integrity error while creating farmer: {str(e)}")
            raise ValueError("Email already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error creating farmer: {str(e)}")
            raise
    
    
    @staticmethod
    def get_farmer_by_id(db: Session, farmer_id: UUID) -> Farmer | None:
        """
        Get a farmer by ID.
        
        Args:
            db: Database session
            farmer_id: UUID of the farmer
            
        Returns:
            Farmer: Farmer object or None if not found
        """
        return db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
    
    
    @staticmethod
    def get_farmer_by_email(db: Session, email: str) -> Farmer | None:
        """
        Get a farmer by email.
        
        Args:
            db: Database session
            email: Email of the farmer
            
        Returns:
            Farmer: Farmer object or None if not found
        """
        return db.query(Farmer).filter(Farmer.email == email).first()
    
    
    @staticmethod
    def get_all_farmers(db: Session, skip: int = 0, limit: int = 100) -> list[Farmer]:
        """
        Get all farmers with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            list[Farmer]: List of farmer objects
        """
        return db.query(Farmer).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def update_farmer(db: Session, farmer_id: UUID, farmer_data: FarmerUpdate) -> Farmer | None:
        """
        Update an existing farmer.
        
        Args:
            db: Database session
            farmer_id: UUID of the farmer to update
            farmer_data: FarmerUpdate schema with updated fields
            
        Returns:
            Farmer: Updated farmer object or None if not found
            
        Raises:
            ValueError: If email already exists
        """
        db_farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        
        if not db_farmer:
            return None
        
        try:
            # Update only provided fields
            update_data = farmer_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_farmer, field, value)
            
            db.commit()
            db.refresh(db_farmer)
            logger.info(f"✓ Farmer updated: {farmer_id}")
            return db_farmer
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"✗ Integrity error while updating farmer: {str(e)}")
            raise ValueError("Email already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error updating farmer: {str(e)}")
            raise
    
    
    @staticmethod
    def delete_farmer(db: Session, farmer_id: UUID) -> bool:
        """
        Delete a farmer.
        
        Args:
            db: Database session
            farmer_id: UUID of the farmer to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        
        if not db_farmer:
            return False
        
        try:
            db.delete(db_farmer)
            db.commit()
            logger.info(f"✓ Farmer deleted: {farmer_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error deleting farmer: {str(e)}")
            raise
    
    
    @staticmethod
    def count_farmers(db: Session) -> int:
        """
        Get total count of farmers.
        
        Args:
            db: Database session
            
        Returns:
            int: Total number of farmers
        """
        return db.query(Farmer).count()