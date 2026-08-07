"""
Workflow Schemas
----------------
Response models for GET /crops/{crop_id}/workflow-status.

The outer shape (crop_id, current_stage, next_stage, days_remaining_in_stage)
is guaranteed by the Workflow Engine and modeled strictly. The inner
guidance sub-objects (irrigation, fertilizer, weed_management) are left
as flexible dicts / extra="allow" models rather than fully typed, because
their exact shape is still evolving in the crop knowledge base JSON
(rice.json vs tomato.json aren't 100% field-identical yet — see the
schema audit) and this endpoint shouldn't reject a valid engine response
just because a crop's JSON has one extra or missing key in a sub-object.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StageInfo(BaseModel):
    """A single growth stage as defined in growth_timeline.stages."""

    stage_id: str
    stage: str
    day_start: int
    day_end: int


class PestAlert(BaseModel):
    """
    A pest relevant to the current stage, expanded from its bare
    {pest_id, risk_level} reference into the full pest record.
    Extra fields (scientific_name, identification, management, etc.)
    pass through even though not individually declared here.
    """

    model_config = ConfigDict(extra="allow")

    pest_id: str
    common_name: Optional[str] = None
    risk_level: Optional[str] = None
    monitor: Optional[bool] = None


class DiseaseAlert(BaseModel):
    """Same idea as PestAlert, for diseases."""

    model_config = ConfigDict(extra="allow")

    disease_id: str
    common_name: Optional[str] = None
    risk_level: Optional[str] = None
    monitor: Optional[bool] = None


class Guidance(BaseModel):
    """Stage-specific guidance payload for the dashboard."""

    objective: Optional[str] = None
    description: Optional[str] = None
    tasks: List[str] = Field(default_factory=list)
    irrigation: Dict[str, Any] = Field(default_factory=dict)
    fertilizer: Dict[str, Any] = Field(default_factory=dict)
    weed_management: Dict[str, Any] = Field(default_factory=dict)
    monitoring: List[str] = Field(default_factory=list)
    pest_alerts: List[PestAlert] = Field(default_factory=list)
    disease_alerts: List[DiseaseAlert] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    expected_crop_status: List[str] = Field(default_factory=list)


class WorkflowStatusResponse(BaseModel):
    """Full response body for GET /crops/{crop_id}/workflow-status."""

    crop_id: str
    current_day: int
    current_stage: StageInfo
    next_stage: Optional[StageInfo] = None
    days_remaining_in_stage: int
    guidance: Guidance