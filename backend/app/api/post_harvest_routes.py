"""
Post-Harvest Routes

GET  /post-harvest/{crop_id}              → latest harvest record + engine assessment
POST /post-harvest/                       → create a harvest record
POST /post-harvest/{crop_id}/storage-log  → log a condition check
"""

import logging
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.post_harvest import (
    HarvestRecordCreate,
    StorageConditionLogCreate,
    StorageConditionLogResponse,
)
from app.services.post_harvest_service import PostHarvestService
from app.services.crop_service import CropService
from app.engines.post_harvest.post_harvest_engine import get_post_harvest_assessment

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/post-harvest",
    tags=["Post-Harvest Intelligence"],
)


# ---------------------------------------------------------------------------
# GET /post-harvest/{crop_id}
# Returns the latest harvest record + latest condition log + engine assessment.
# The StorageStatusCard in the dashboard calls this single endpoint.
# ---------------------------------------------------------------------------
@router.get("/{crop_id}")
def get_post_harvest_status(crop_id: UUID, db: Session = Depends(get_db)):
    crop = CropService.get_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found.")

    record = PostHarvestService.get_latest_harvest_by_crop(db, crop_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="No harvest record found for this crop.",
        )

    latest_log = PostHarvestService.get_latest_log(db, record.harvest_id)
    days_in_storage = (date.today() - record.harvest_date).days

    assessment = get_post_harvest_assessment(
        crop_type=crop.crop_type,
        storage_type=record.storage_type,
        days_in_storage=max(0, days_in_storage),
        quantity_kg=record.quantity_kg,
        harvest_id=record.harvest_id,
        latest_log=latest_log.to_dict() if latest_log else None,
    )

    return {
        # Harvest record fields
        "harvest_id": str(record.harvest_id),
        "harvest_date": record.harvest_date.isoformat(),
        "quantity_kg": record.quantity_kg,
        "storage_type": record.storage_type,
        "storage_location": record.storage_location,
        "latest_log": latest_log.to_dict() if latest_log else None,
        # Engine output (flat — UI reads top-level keys directly)
        **{k: v for k, v in assessment.items() if k not in ("harvest_id", "latest_log")},
    }


# ---------------------------------------------------------------------------
# POST /post-harvest/
# Create a harvest record. Called by the new form in StorageStatusCard.
# ---------------------------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_harvest_record(data: HarvestRecordCreate, db: Session = Depends(get_db)):
    crop = CropService.get_crop_by_id(db, data.crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {data.crop_id} not found.")

    record = PostHarvestService.create_harvest_record(db, data)
    logger.info(f"Harvest record created: {record.harvest_id} for crop {data.crop_id}")
    return record.to_dict()


# ---------------------------------------------------------------------------
# POST /post-harvest/{crop_id}/storage-log
# Log a condition check against the latest harvest record for this crop.
# Called by ConditionLogForm in the dashboard.
# ---------------------------------------------------------------------------
@router.post("/{crop_id}/storage-log", status_code=status.HTTP_201_CREATED)
def log_storage_condition(
    crop_id: UUID,
    data: StorageConditionLogCreate,
    db: Session = Depends(get_db),
):
    record = PostHarvestService.get_latest_harvest_by_crop(db, crop_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="No harvest record found for this crop. Create one first.",
        )

    log = PostHarvestService.create_condition_log(db, record, data)
    return StorageConditionLogResponse.model_validate(log)