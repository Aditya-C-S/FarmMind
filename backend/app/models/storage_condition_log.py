"""
StorageConditionLog model for FarmMind backend.
One row per storage check-in — captures environmental readings and
visual observations at a point in time after harvest.
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class StorageConditionLog(Base):
    """
    Represents a single storage condition check for a harvest record.
    days_in_storage is stored directly as supplied by the caller
    (calculated from harvest_date on the route layer so the engine
    never has to re-derive it from the DB).
    """

    __tablename__ = "storage_condition_logs"

    # Primary Key
    log_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Key
    harvest_id = Column(
        UUID(as_uuid=True),
        ForeignKey("harvest_records.harvest_id", ondelete="CASCADE"),
        nullable=False,
    )

    # When this check was recorded
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Environmental readings
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)

    # Derived at record time: (recorded_at.date - harvest_date).days
    days_in_storage = Column(Integer, nullable=False)

    # Visual observation
    # Allowed values: good | early_spoilage | critical
    visual_condition = Column(String(20), nullable=False, default="good")

    # Free-text farmer notes
    notes = Column(Text, nullable=True)

    # Relationships
    harvest_record = relationship("HarvestRecord", back_populates="condition_logs")

    def __repr__(self) -> str:
        return (
            f"<StorageConditionLog(log_id={self.log_id}, "
            f"harvest_id={self.harvest_id}, days={self.days_in_storage}, "
            f"condition='{self.visual_condition}')>"
        )

    def to_dict(self) -> dict:
        return {
            "log_id": str(self.log_id),
            "harvest_id": str(self.harvest_id),
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "temperature_c": self.temperature_c,
            "humidity_percent": self.humidity_percent,
            "days_in_storage": self.days_in_storage,
            "visual_condition": self.visual_condition,
            "notes": self.notes,
        }