"""
app/api/decision_optimization_routes.py

Route for the Decision Optimization stage: Context Fusion -> Alternative
Builder -> AHP -> TOPSIS -> ranked action list.

Mirrors the structure of workflow_routes.py and context_fusion_routes.py —
same crop lookup, same db.query(Field)... shortcut for coordinates, same
engine-exception -> HTTP status mapping pattern.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.crop_service import CropService
from app.models.field import Field
from app.engines.workflow import get_daily_workflow
from app.engines.context_fusion import get_fused_context
from app.engines.decision_optimization import get_ranked_actions
from app.engines.workflow.crop_loader import CropLoadError, CropNotFoundError
from app.engines.workflow.guideline_loader import GuidelineNotFoundError
from app.engines.workflow.stage_resolver import StageNotFoundError
from app.schemas.context_fusion import ContextFusionRequest


router = APIRouter(tags=["Decision Optimization"])


@router.post("/crops/{crop_id}/recommendations")
def get_recommendations(
    crop_id: UUID,
    body: ContextFusionRequest = ContextFusionRequest(),
    as_of: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """
    Runs the full Decision Optimization pipeline for one crop and returns
    a ranked list of candidate actions.

    Body: {"detections": [...]}  — same shape as /context-status, list of
        run_pipeline()-style dicts, omit/empty if no photo analyzed yet.
    Query: ?as_of=YYYY-MM-DD      — defaults to today if omitted.
    """
    crop = CropService.get_crop_by_id(db, crop_id)
    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Crop not found."
        )

    if not crop.sowing_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This crop has no sowing date set — the engine needs one to place it on the timeline.",
        )

    # Same direct-query shortcut context_fusion_routes.py already uses —
    # consolidate into a FieldService call later if one turns out to exist
    # (see open item #1 in the project handoff).
    field = db.query(Field).filter(Field.field_id == crop.field_id).first()
    latitude = field.latitude if field else None
    longitude = field.longitude if field else None

    crop_type = crop.crop_type.lower()

    # --- Context Fusion (weather + disease + activity) -----------------
    try:
        fused_context = get_fused_context(
            db=db,
            crop_id=crop.crop_id,
            latitude=latitude,
            longitude=longitude,
            crop_type=crop_type,
            sowing_date=crop.sowing_date,
            detections=[d.model_dump() for d in body.detections],
            as_of=as_of,
        )
    except CropNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No knowledge base exists for crop type '{crop.crop_type}': {e}",
        ) from e
    except CropLoadError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge base for '{crop.crop_type}' is corrupted: {e}",
        ) from e
    except StageNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except GuidelineNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge base inconsistency for '{crop.crop_type}': {e}",
        ) from e

    # --- Workflow, best-effort ------------------------------------------
    # Only used inside build_alternatives() as a fallback source of
    # pending-task text if fused_context doesn't already carry it. Not
    # fatal if this call fails — fused_context is the primary source, and
    # a broken fallback shouldn't take down the whole recommendation.
    workflow = None
    try:
        workflow = get_daily_workflow(crop.crop_id, crop.sowing_date, today=as_of)
    except Exception:
        workflow = None

    # --- Decision Optimization (Alternative Builder -> AHP -> TOPSIS) ---
    ranked_actions = get_ranked_actions(fused_context, workflow=workflow)

    return {
        "crop_id": str(crop_id),
        "as_of": str(as_of) if as_of else None,
        "actions": ranked_actions,
        "guidance": fused_context.get("guidance", {}),
        "weather": fused_context.get("weather_context", {}).get("forecast", []),
    }
