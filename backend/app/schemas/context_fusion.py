"""
Context Fusion Schemas
----------------------
Request/response models for POST /crops/{crop_id}/context-status.

Reuses StageInfo and Guidance from the Workflow Engine's schemas rather
than redefining them — those shapes are stable and already validated.
The three *_context sub-objects (weather, activity, disease) are kept as
loosely-typed dicts since Context Fusion is brand new and those shapes
may still shift as real farm data and Aditya's model surface edge cases
we haven't seen yet.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.workflow import Guidance as WorkflowGuidance, StageInfo

class DetectionInput(BaseModel):
    """
    One disease detection result, shaped exactly like run_pipeline()'s
    output. The caller (frontend, or whatever glue calls Aditya's
    pipeline) is responsible for producing this — this route never calls
    his pipeline directly.
    """

    model_config = ConfigDict(extra="allow")

    disease: str
    crop: Optional[str] = None
    confidence: Optional[float] = None
    severity_score: Optional[float] = None
    severity_class: Optional[str] = None
    occurrence_prob: Optional[float] = None
    progression: Optional[str] = None
    economic_loss: Optional[Dict[str, Any]] = None

class ContextGuidance(BaseModel):
    workflow: WorkflowGuidance
    irrigation: Optional[Dict[str, Any]] = None
    disease_prevention: List[Dict[str, Any]] = Field(default_factory=list)

class ContextFusionRequest(BaseModel):
    """Request body. Omit or send an empty list if no photo has been analyzed yet."""

    detections: List[DetectionInput] = Field(default_factory=list)


class ContextFusionResponse(BaseModel):
    """Full response body for POST /crops/{crop_id}/context-status."""

    crop_id: str
    current_stage: StageInfo
    next_stage: Optional[StageInfo] = None
    days_remaining_in_stage: int
    guidance: ContextGuidance
    weather_context: Dict[str, Any]
    activity_context: Dict[str, Any]
    disease_context: Dict[str, Any]

