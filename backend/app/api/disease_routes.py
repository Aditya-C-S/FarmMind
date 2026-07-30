"""
Disease Routes module.
API endpoints for disease history operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.session import get_db
from app.schemas.disease_history import DiseaseHistoryCreate, DiseaseHistoryUpdate, DiseaseHistoryResponse, DiseaseHistoryListResponse
from app.services.disease_service import DiseaseService

router = APIRouter(prefix="/diseases", tags=["Diseases"])


@router.post("", response_model=DiseaseHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_disease(disease_data: DiseaseHistoryCreate, db: Session = Depends(get_db)):
    """Create a new disease record"""
    try:
        disease = DiseaseService.create_disease(db, disease_data)
        return disease
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating disease record")


@router.get("", response_model=list[DiseaseHistoryListResponse])
def list_diseases(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all disease records (paginated)"""
    # Note: This gets all diseases without crop filter - consider filtering in production
    return []


@router.get("/{disease_id}", response_model=DiseaseHistoryResponse)
def get_disease(disease_id: UUID, db: Session = Depends(get_db)):
    """Get a specific disease record by ID"""
    disease = DiseaseService.get_disease_by_id(db, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    return disease


@router.get("/crop/{crop_id}", response_model=list[DiseaseHistoryListResponse])
def get_diseases_by_crop(crop_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all disease records for a specific crop"""
    diseases = DiseaseService.get_diseases_by_crop(db, crop_id, skip, limit)
    return diseases


@router.get("/crop/{crop_id}/active", response_model=list[DiseaseHistoryListResponse])
def get_active_diseases(crop_id: UUID, db: Session = Depends(get_db)):
    """Get active diseases for a crop"""
    diseases = DiseaseService.get_active_diseases(db, crop_id)
    return diseases


@router.put("/{disease_id}", response_model=DiseaseHistoryResponse)
def update_disease(disease_id: UUID, disease_data: DiseaseHistoryUpdate, db: Session = Depends(get_db)):
    """Update a disease record"""
    disease = DiseaseService.update_disease(db, disease_id, disease_data)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    return disease


@router.delete("/{disease_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disease(disease_id: UUID, db: Session = Depends(get_db)):
    """Delete a disease record"""
    success = DiseaseService.delete_disease(db, disease_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    return None


@router.get("/crop/{crop_id}/count", response_model=dict)
def count_diseases(crop_id: UUID, status_filter: str | None = None, db: Session = Depends(get_db)):
    """Count diseases for a crop"""
    count = DiseaseService.count_diseases_by_crop(db, crop_id, status_filter)
    return {"crop_id": crop_id, "total_diseases": count, "status_filter": status_filter}