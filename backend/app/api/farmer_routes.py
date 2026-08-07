"""
Farmer API routes.
Exposes farmer CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from app.services.farmer_service import FarmerService

# Create router
router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=FarmerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new farmer",
    description="Create a new farmer in the system"
)
def create_farmer(
    farmer: FarmerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new farmer.
    
    **Required fields:**
    - name: Farmer's full name
    - phone: Phone number (10-15 digits)
    - email: Valid email address (must be unique)
    - district: District name
    - state: State name
    """
    try:
        return FarmerService.create_farmer(db, farmer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create farmer"
        )


@router.get(
    "",
    response_model=list[FarmerResponse],
    summary="Get all farmers",
    description="Retrieve all farmers with pagination"
)
def get_all_farmers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all farmers with pagination.
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return FarmerService.get_all_farmers(db, skip=skip, limit=limit)


@router.get(
    "/{farmer_id}",
    response_model=FarmerResponse,
    summary="Get farmer by ID",
    description="Retrieve a specific farmer by their ID"
)
def get_farmer(
    farmer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a farmer by their ID.
    
    **Path parameters:**
    - farmer_id: UUID of the farmer
    """
    farmer = FarmerService.get_farmer_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return farmer


@router.put(
    "/{farmer_id}",
    response_model=FarmerResponse,
    summary="Update farmer",
    description="Update farmer details"
)
def update_farmer(
    farmer_id: UUID,
    farmer_update: FarmerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update farmer details.
    
    **Path parameters:**
    - farmer_id: UUID of the farmer to update
    
    **Body:** Provide only the fields you want to update
    """
    farmer = FarmerService.update_farmer(db, farmer_id, farmer_update)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return farmer


@router.delete(
    "/{farmer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete farmer",
    description="Delete a farmer (cascades to fields and crops)"
)
def delete_farmer(
    farmer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a farmer.
    
    **Warning:** Deleting a farmer will also delete all their fields and crops!
    
    **Path parameters:**
    - farmer_id: UUID of the farmer to delete
    """
    deleted = FarmerService.delete_farmer(db, farmer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return None


@router.get(
    "/count/total",
    summary="Count farmers",
    description="Get total number of farmers"
)
def count_farmers(db: Session = Depends(get_db)):
    """Get total count of farmers in the system"""
    count = FarmerService.count_farmers(db)
    return {"total_farmers": count}