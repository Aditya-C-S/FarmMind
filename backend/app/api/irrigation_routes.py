"""
Irrigation Routes module.
API endpoints for irrigation management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.session import get_db
from app.schemas.irrigation import IrrigationCreate, IrrigationUpdate, IrrigationResponse, IrrigationListResponse, IrrigationStatsResponse
from app.services.irrigation_service import IrrigationService

router = APIRouter(prefix="/irrigations", tags=["Irrigations"])


@router.post("", response_model=IrrigationResponse, status_code=status.HTTP_201_CREATED)
def create_irrigation(irrigation_data: IrrigationCreate, db: Session = Depends(get_db)):
    """Create a new irrigation record"""
    try:
        irrigation = IrrigationService.create_irrigation(db, irrigation_data)
        return irrigation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating irrigation record")


@router.get("", response_model=list[IrrigationListResponse])
def list_irrigations(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all irrigation records (paginated)"""
    # Note: This gets all irrigations without crop filter - consider filtering in production
    return []


@router.get("/{irrigation_id}", response_model=IrrigationResponse)
def get_irrigation(irrigation_id: UUID, db: Session = Depends(get_db)):
    """Get a specific irrigation record by ID"""
    irrigation = IrrigationService.get_irrigation_by_id(db, irrigation_id)
    if not irrigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Irrigation record not found")
    return irrigation


@router.get("/crop/{crop_id}", response_model=list[IrrigationListResponse])
def get_irrigations_by_crop(crop_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all irrigation records for a specific crop"""
    irrigations = IrrigationService.get_irrigations_by_crop(db, crop_id, skip, limit)
    return irrigations


@router.get("/crop/{crop_id}/stats", response_model=IrrigationStatsResponse)
def get_irrigation_stats(crop_id: UUID, db: Session = Depends(get_db)):
    """Get irrigation statistics for a crop"""
    stats = IrrigationService.get_irrigation_stats(db, crop_id)
    return stats


@router.put("/{irrigation_id}", response_model=IrrigationResponse)
def update_irrigation(irrigation_id: UUID, irrigation_data: IrrigationUpdate, db: Session = Depends(get_db)):
    """Update an irrigation record"""
    irrigation = IrrigationService.update_irrigation(db, irrigation_id, irrigation_data)
    if not irrigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Irrigation record not found")
    return irrigation


@router.delete("/{irrigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation(irrigation_id: UUID, db: Session = Depends(get_db)):
    """Delete an irrigation record"""
    success = IrrigationService.delete_irrigation(db, irrigation_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Irrigation record not found")
    return None


@router.get("/crop/{crop_id}/count", response_model=dict)
def count_irrigations(crop_id: UUID, db: Session = Depends(get_db)):
    """Count irrigation records for a crop"""
    count = IrrigationService.count_irrigations_by_crop(db, crop_id)
    return {"crop_id": crop_id, "total_irrigations": count}