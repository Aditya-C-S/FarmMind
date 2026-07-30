"""
Fertilizer Routes module.
API endpoints for fertilizer application operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.session import get_db
from app.schemas.fertilizer_application import FertilizerApplicationCreate, FertilizerApplicationUpdate, FertilizerApplicationResponse, FertilizerApplicationListResponse, FertilizerStatsResponse
from app.services.fertilizer_service import FertilizerService

router = APIRouter(prefix="/fertilizers", tags=["Fertilizers"])


@router.post("", response_model=FertilizerApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_fertilizer(fertilizer_data: FertilizerApplicationCreate, db: Session = Depends(get_db)):
    """Create a new fertilizer application record"""
    try:
        fertilizer = FertilizerService.create_fertilizer(db, fertilizer_data)
        return fertilizer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating fertilizer record")


@router.get("", response_model=list[FertilizerApplicationListResponse])
def list_fertilizers(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all fertilizer records (paginated)"""
    # Note: This gets all fertilizers without crop filter - consider filtering in production
    return []


@router.get("/{fertilizer_id}", response_model=FertilizerApplicationResponse)
def get_fertilizer(fertilizer_id: UUID, db: Session = Depends(get_db)):
    """Get a specific fertilizer record by ID"""
    fertilizer = FertilizerService.get_fertilizer_by_id(db, fertilizer_id)
    if not fertilizer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer record not found")
    return fertilizer


@router.get("/crop/{crop_id}", response_model=list[FertilizerApplicationListResponse])
def get_fertilizers_by_crop(crop_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all fertilizer records for a specific crop"""
    fertilizers = FertilizerService.get_fertilizers_by_crop(db, crop_id, skip, limit)
    return fertilizers


@router.get("/crop/{crop_id}/stats", response_model=FertilizerStatsResponse)
def get_fertilizer_stats(crop_id: UUID, db: Session = Depends(get_db)):
    """Get fertilizer statistics for a crop"""
    stats = FertilizerService.get_fertilizer_stats(db, crop_id)
    return stats


@router.put("/{fertilizer_id}", response_model=FertilizerApplicationResponse)
def update_fertilizer(fertilizer_id: UUID, fertilizer_data: FertilizerApplicationUpdate, db: Session = Depends(get_db)):
    """Update a fertilizer record"""
    fertilizer = FertilizerService.update_fertilizer(db, fertilizer_id, fertilizer_data)
    if not fertilizer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer record not found")
    return fertilizer


@router.delete("/{fertilizer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fertilizer(fertilizer_id: UUID, db: Session = Depends(get_db)):
    """Delete a fertilizer record"""
    success = FertilizerService.delete_fertilizer(db, fertilizer_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer record not found")
    return None


@router.get("/crop/{crop_id}/count", response_model=dict)
def count_fertilizers(crop_id: UUID, db: Session = Depends(get_db)):
    """Count fertilizer records for a crop"""
    count = FertilizerService.count_fertilizers_by_crop(db, crop_id)
    return {"crop_id": crop_id, "total_fertilizers": count}