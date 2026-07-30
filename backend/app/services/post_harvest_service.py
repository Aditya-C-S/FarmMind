"""
Post-Harvest Service — DB CRUD for HarvestRecord and StorageConditionLog.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime
from typing import Optional

from app.models.harvest_record import HarvestRecord
from app.models.storage_condition_log import StorageConditionLog
from app.schemas.post_harvest import HarvestRecordCreate, StorageConditionLogCreate


class PostHarvestService:

    # ── HarvestRecord ────────────────────────────────────────────────────────

    @staticmethod
    def create_harvest_record(db: Session, data: HarvestRecordCreate) -> HarvestRecord:
        record = HarvestRecord(
            crop_id=data.crop_id,
            harvest_date=data.harvest_date,
            quantity_kg=data.quantity_kg,
            storage_type=data.storage_type.value,
            storage_location=data.storage_location,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_latest_harvest_by_crop(db: Session, crop_id: UUID) -> Optional[HarvestRecord]:
        """Return the most recent harvest record for a crop."""
        return (
            db.query(HarvestRecord)
            .filter(HarvestRecord.crop_id == crop_id)
            .order_by(HarvestRecord.harvest_date.desc())
            .first()
        )

    @staticmethod
    def get_harvest_by_id(db: Session, harvest_id: UUID) -> Optional[HarvestRecord]:
        return db.query(HarvestRecord).filter(HarvestRecord.harvest_id == harvest_id).first()

    # ── StorageConditionLog ──────────────────────────────────────────────────

    @staticmethod
    def create_condition_log(
        db: Session,
        harvest_record: HarvestRecord,
        data: StorageConditionLogCreate,
    ) -> StorageConditionLog:
        days = (date.today() - harvest_record.harvest_date).days
        log = StorageConditionLog(
            harvest_id=harvest_record.harvest_id,
            recorded_at=datetime.utcnow(),
            temperature_c=data.temperature_c,
            humidity_percent=data.humidity_percent,
            days_in_storage=max(0, days),
            visual_condition=data.visual_condition.value,
            notes=data.notes,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_latest_log(db: Session, harvest_id: UUID) -> Optional[StorageConditionLog]:
        return (
            db.query(StorageConditionLog)
            .filter(StorageConditionLog.harvest_id == harvest_id)
            .order_by(StorageConditionLog.recorded_at.desc())
            .first()
        )