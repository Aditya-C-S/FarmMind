"""
Context Fusion Engine
---------------------
Top-level orchestrator for Phase 4:

    Workflow Engine (expected: stage + tasks + typical pest/disease risk)
        + real weather data (Phase 2)
        + real logged farmer activity (Phase 2)
        + real disease detection (Aditya's pipeline — kept as a plain
          parameter, never imported here directly)
    -> one merged picture of what's actually happening on this crop

Disease detection is deliberately NOT imported or called from inside this
engine. The caller (e.g. an API route, or a script) is responsible for
obtaining `detections` — by calling Aditya's run_pipeline() on an uploaded
photo, or passing an empty list if no photo has been analyzed yet. This
means Context Fusion works fully today, with zero dependency on his code
being finished, exactly like crop_loader doesn't care whether a knowledge
base file was authored by hand or merged from five files.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.engines.context_fusion.activity_context import get_activity_context
from app.engines.context_fusion.disease_context import get_disease_context
from app.engines.context_fusion.fusion_response_builder import build_fusion_response
from app.engines.context_fusion.weather_context import get_weather_context
from app.engines.workflow import get_daily_workflow
from app.engines.workflow.crop_loader import load_crop


def get_fused_context(
    db: Session,
    crop_id: UUID,
    latitude: Optional[float],
    longitude: Optional[float],
    crop_type: str,
    sowing_date: date,
    detections: Optional[List[Dict[str, Any]]] = None,
    as_of: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Build the fully merged context for a planted crop.

    Args:
        db: SQLAlchemy session (used for activity lookups only — weather
            now comes from a live Open-Meteo call, not our own DB; see
            weather_context.py for why)
        crop_id: the planted Crop record's UUID (for activity lookups)
        latitude, longitude: the crop's field coordinates, for the live
                  weather lookup. Pass None for either if the field has no
                  recorded coordinates — weather_context will report
                  data_available=False rather than fail the whole request.
        crop_type: e.g. "rice", "tomato" — same value passed to the
                   Workflow Engine
        sowing_date: the crop's sowing date
        detections: list of run_pipeline()-shaped dicts from Aditya's
                    disease detection pipeline, or None/[] if no photo has
                    been analyzed yet
        as_of: reference date; defaults to today

    Returns:
        Merged context — see fusion_response_builder.build_fusion_response()

    Raises:
        Propagates the same exceptions as get_daily_workflow() —
        CropNotFoundError, CropLoadError, StageNotFoundError,
        GuidelineNotFoundError — since this always resolves the workflow
        first before fusing in the other contexts.
    """
    workflow_result = get_daily_workflow(crop_id=crop_type, sowing_date=sowing_date, today=as_of)

    # Reuses crop_loader's in-memory cache — this is not a second file read
    crop_data = load_crop(crop_type)

    weather = get_weather_context(latitude, longitude, crop_type, workflow_result["current_stage"]["stage"], crop_data, as_of=as_of)
    activity = get_activity_context(db, crop_id, workflow_result["guidance"]["tasks"], as_of=as_of)
    disease = get_disease_context(workflow_result["guidance"]["disease_alerts"], detections or [])

    return build_fusion_response(workflow_result, weather, activity, disease)