"""
Pydantic schemas for Post-Harvest Intelligence.
Covers HarvestRecord CRUD, StorageConditionLog CRUD, and the
engine's assessment response.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from enum import Enum


# ---------------------------------------------------------------------------
# Enums — validated at API boundary so invalid values are rejected with 422
# ---------------------------------------------------------------------------

class StorageType(str, Enum):
    COLD_ROOM = "cold_room"
    AMBIENT = "ambient"
    COVERED_SHED = "covered_shed"
    OPEN = "open"


class VisualCondition(str, Enum):
    GOOD = "good"
    EARLY_SPOILAGE = "early_spoilage"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# HarvestRecord schemas
# ---------------------------------------------------------------------------

class HarvestRecordCreate(BaseModel):
    crop_id: UUID
    harvest_date: date
    quantity_kg: float = Field(..., gt=0, description="Harvested quantity in kg")
    storage_type: StorageType
    storage_location: Optional[str] = Field(None, max_length=200)

    @field_validator("quantity_kg")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity_kg must be positive")
        return v


class HarvestRecordUpdate(BaseModel):
    harvest_date: Optional[date] = None
    quantity_kg: Optional[float] = Field(None, gt=0)
    storage_type: Optional[StorageType] = None
    storage_location: Optional[str] = Field(None, max_length=200)


class HarvestRecordResponse(BaseModel):
    harvest_id: UUID
    crop_id: UUID
    harvest_date: date
    quantity_kg: float
    storage_type: str
    storage_location: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# StorageConditionLog schemas
# ---------------------------------------------------------------------------

class StorageConditionLogCreate(BaseModel):
    """
    Caller supplies the readings.
    days_in_storage is calculated on the route layer from harvest_date
    so the engine always works with a pre-computed integer.
    """
    temperature_c: Optional[float] = Field(None, ge=-10, le=60)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    visual_condition: VisualCondition = VisualCondition.GOOD
    notes: Optional[str] = None


class StorageConditionLogResponse(BaseModel):
    log_id: UUID
    harvest_id: UUID
    recorded_at: datetime
    temperature_c: Optional[float]
    humidity_percent: Optional[float]
    days_in_storage: int
    visual_condition: str
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Post-Harvest Assessment response (engine output)
# ---------------------------------------------------------------------------

class StorageHealthStatus(str, Enum):
    OPTIMAL = "optimal"
    ACCEPTABLE = "acceptable"
    AT_RISK = "at_risk"
    CRITICAL = "critical"

class StorageHealth(BaseModel):

    overall_status: StorageHealthStatus

    temperature_ok: Optional[bool] = None

    humidity_ok: Optional[bool] = None

    moisture_ok: Optional[bool] = None

    out_of_range_params: List[str] = []


class SpoilageRisk(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentRecommendation(BaseModel):
    priority: int                  # 1 = most urgent
    action: str
    reason: str
    urgency: str                   # immediate | within_24h | within_week | routine


class PostHarvestAssessment(BaseModel):
    """
    Full engine output for a single harvest record.
    All fields are rule-derived — no ML involved.
    """
    harvest_id: UUID
    crop_type: str
    storage_type: str
    days_in_storage: int
    quantity_kg: float

    # Shelf life
    estimated_shelf_life_days: int
    remaining_shelf_life_days: int
    shelf_life_consumed_percent: float

    # Storage health based on latest condition log
    storage_health: StorageHealthStatus
    spoilage_risk: SpoilageRisk

    # Human-readable summary
    health_summary: str
    spoilage_summary: str

    # Factors that drove the assessment
    risk_factors: List[str]

    # Ordered action list
    recommendations: List[AssessmentRecommendation]

    # Raw condition snapshot used for the assessment
    latest_log: Optional[StorageConditionLogResponse]

    # Knowledge-base storage best practices for this crop
    storage_best_practices: List[str]

# ---------------------------------------------------------------------------
# Dashboard Response
# Combines Harvest Record + Latest Storage Log + Engine Assessment
# Used by GET /post-harvest/{crop_id}
# ---------------------------------------------------------------------------
class StorageRecommendation(BaseModel):

    recommended_storage: str

    reason: str

    expected_shelf_life_days: int

    recommended_practices: List[str]

    before_storage_checklist: List[str]

class DashboardPostHarvestResponse(BaseModel):
    # Harvest Information
    harvest_id: UUID
    crop_id: UUID
    harvest_date: date
    quantity_kg: float
    storage_type: str
    storage_location: Optional[str]

    # Latest Storage Log
    latest_log: Optional[StorageConditionLogResponse]

    # Engine Assessment
    days_in_storage: int

    base_shelf_life_days: int
    remaining_shelf_life_days: int
    shelf_life_pct_remaining: float
    stress_days_accumulated: int

    storage_health: StorageHealth
    spoilage_risk_level: SpoilageRisk
    spoilage_risk_score: float

    health_summary: str
    spoilage_summary: str

    spoilage_signs_to_watch: List[str]

    ranked_actions: List[AssessmentRecommendation]
    recommendation: StorageRecommendation

    best_practices: List[str]

    model_config = {"from_attributes": True}