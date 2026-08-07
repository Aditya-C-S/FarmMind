"""
HarvestRecord model for FarmMind backend.
One row per harvest event — links a crop to its post-harvest lifecycle.
"""

from sqlalchemy import Column, String, Date, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class HarvestRecord(Base):
    """
    Represents a single harvest event for a crop.
    Parent to StorageConditionLog — one harvest can have many condition checks.
    """

    __tablename__ = "harvest_records"

    # Primary Key
    harvest_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Key
    crop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("crops.crop_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Harvest details
    harvest_date = Column(Date, nullable=False)
    quantity_kg = Column(Float, nullable=False)

    # Storage setup at the time of harvest
    # Allowed values: cold_room | ambient | covered_shed | open
    storage_type = Column(String(30), nullable=False)
    storage_location = Column(String(200), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    crop = relationship("Crop", back_populates="harvest_records")
    condition_logs = relationship(
        "StorageConditionLog",
        back_populates="harvest_record",
        cascade="all, delete-orphan",
        order_by="StorageConditionLog.recorded_at",
    )

    def __repr__(self) -> str:
        return (
            f"<HarvestRecord(harvest_id={self.harvest_id}, "
            f"crop_id={self.crop_id}, harvest_date={self.harvest_date})>"
        )

    def to_dict(self) -> dict:
        return {
            "harvest_id": str(self.harvest_id),
            "crop_id": str(self.crop_id),
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "quantity_kg": self.quantity_kg,
            "storage_type": self.storage_type,
            "storage_location": self.storage_location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }