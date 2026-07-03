"""
Field API routes.
Exposes field CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from app.services.field_service import FieldService

# Create router
router = APIRouter(
    prefix="/fields",
    tags=["Fields"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new field",
    description="Create a new field for a farmer"
)
def create_field(
    field: FieldCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new field.
    
    **Required fields:**
    - farmer_id: UUID of the farmer who owns this field
    - field_name: Name of the field
    - area_acres: Area of the field in acres (must be > 0)
    
    **Optional fields:**
    - soil_type: Type of soil
    - latitude: Latitude coordinate (-90 to 90)
    - longitude: Longitude coordinate (-180 to 180)
    """
    try:
        return FieldService.create_field(db, field)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create field"
        )


@router.get(
    "",
    response_model=list[FieldResponse],
    summary="Get all fields",
    description="Retrieve all fields with pagination"
)
def get_all_fields(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all fields with pagination.
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return FieldService.get_all_fields(db, skip=skip, limit=limit)


@router.get(
    "/{field_id}",
    response_model=FieldResponse,
    summary="Get field by ID",
    description="Retrieve a specific field by its ID"
)
def get_field(
    field_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a field by its ID.
    
    **Path parameters:**
    - field_id: UUID of the field
    """
    field = FieldService.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID {field_id} not found"
        )
    return field


@router.get(
    "/farmer/{farmer_id}",
    response_model=list[FieldResponse],
    summary="Get farmer's fields",
    description="Get all fields owned by a specific farmer"
)
def get_farmer_fields(
    farmer_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all fields owned by a specific farmer.
    
    **Path parameters:**
    - farmer_id: UUID of the farmer
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    return FieldService.get_fields_by_farmer(db, farmer_id, skip=skip, limit=limit)


@router.put(
    "/{field_id}",
    response_model=FieldResponse,
    summary="Update field",
    description="Update field details"
)
def update_field(
    field_id: UUID,
    field_update: FieldUpdate,
    db: Session = Depends(get_db)
):
    """
    Update field details.
    
    **Path parameters:**
    - field_id: UUID of the field to update
    
    **Body:** Provide only the fields you want to update
    """
    field = FieldService.update_field(db, field_id, field_update)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID {field_id} not found"
        )
    return field


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete field",
    description="Delete a field (cascades to crops)"
)
def delete_field(
    field_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a field.
    
    **Warning:** Deleting a field will also delete all crops grown in that field!
    
    **Path parameters:**
    - field_id: UUID of the field to delete
    """
    deleted = FieldService.delete_field(db, field_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID {field_id} not found"
        )
    return None


@router.get(
    "/count/total",
    summary="Count fields",
    description="Get total number of fields"
)
def count_fields(
    farmer_id: UUID | None = Query(None, description="Optional: count fields for specific farmer"),
    db: Session = Depends(get_db)
):
    """Get total count of fields in the system (optionally filtered by farmer)"""
    count = FieldService.count_fields(db, farmer_id=farmer_id)
    return {"total_fields": count}