"""
Crop API routes.
Exposes crop CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from app.database import get_db
from app.schemas.crop import CropCreate, CropUpdate, CropResponse
from app.services.crop_service import CropService

# Create router
router = APIRouter(
    prefix="/crops",
    tags=["Crops"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=CropResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new crop",
    description="Create a new crop in a field"
)
def create_crop(
    crop: CropCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new crop.
    
    **Required fields:**
    - field_id: UUID of the field where crop will be grown
    - crop_type: Type of crop (e.g., Rice, Tomato)
    - sowing_date: Date when crop will be sown
    - expected_harvest_date: Expected harvest date (must be after sowing date)
    
    **Optional fields:**
    - variety: Variety of crop (e.g., IR-64, Arka Samrat)
    """
    try:
        return CropService.create_crop(db, crop)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create crop"
        )


@router.get(
    "",
    response_model=list[CropResponse],
    summary="Get all crops",
    description="Retrieve all crops with pagination"
)
def get_all_crops(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all crops with pagination.
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return CropService.get_all_crops(db, skip=skip, limit=limit)


@router.get(
    "/{crop_id}",
    response_model=CropResponse,
    summary="Get crop by ID",
    description="Retrieve a specific crop by its ID"
)
def get_crop(
    crop_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a crop by its ID.
    
    **Path parameters:**
    - crop_id: UUID of the crop
    """
    crop = CropService.get_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )
    return crop


@router.get(
    "/field/{field_id}",
    response_model=list[CropResponse],
    summary="Get field's crops",
    description="Get all crops grown in a specific field"
)
def get_field_crops(
    field_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all crops grown in a specific field.
    
    **Path parameters:**
    - field_id: UUID of the field
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return CropService.get_crops_by_field(db, field_id, skip=skip, limit=limit)


@router.get(
    "/farmer/{farmer_id}",
    response_model=list[CropResponse],
    summary="Get farmer's crops",
    description="Get all crops owned by a specific farmer"
)
def get_farmer_crops(
    farmer_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all crops owned by a specific farmer.
    
    **Path parameters:**
    - farmer_id: UUID of the farmer
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return CropService.get_crops_by_farmer(db, farmer_id, skip=skip, limit=limit)


@router.get(
    "/type/{crop_type}",
    response_model=list[CropResponse],
    summary="Get crops by type",
    description="Get all crops of a specific type"
)
def get_crops_by_type(
    crop_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all crops of a specific type (e.g., Rice, Tomato).
    
    **Path parameters:**
    - crop_type: Type of crop
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return CropService.get_crops_by_type(db, crop_type, skip=skip, limit=limit)


@router.put(
    "/{crop_id}",
    response_model=CropResponse,
    summary="Update crop",
    description="Update crop details"
)
def update_crop(
    crop_id: UUID,
    crop_update: CropUpdate,
    db: Session = Depends(get_db)
):
    """
    Update crop details.
    
    **Path parameters:**
    - crop_id: UUID of the crop to update
    
    **Body:** Provide only the fields you want to update
    """
    crop = CropService.update_crop(db, crop_id, crop_update)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )
    return crop


@router.delete(
    "/{crop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete crop",
    description="Delete a crop"
)
def delete_crop(
    crop_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a crop.
    
    **Path parameters:**
    - crop_id: UUID of the crop to delete
    """
    deleted = CropService.delete_crop(db, crop_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found"
        )
    return None


@router.get(
    "/count/total",
    summary="Count crops",
    description="Get total number of crops"
)
def count_crops(
    field_id: UUID | None = Query(None, description="Optional: count crops in specific field"),
    farmer_id: UUID | None = Query(None, description="Optional: count crops owned by farmer"),
    db: Session = Depends(get_db)
):
    """
    Get total count of crops in the system.
    
    **Query parameters:**
    - field_id: Optional - count crops in specific field
    - farmer_id: Optional - count crops owned by farmer
    """
    count = CropService.count_crops(db, field_id=field_id, farmer_id=farmer_id)
    return {"total_crops": count}