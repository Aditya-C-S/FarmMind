"""
Workflow Routes
----------------
GET /crops/{crop_id}/workflow-status

This is the only place the DB world and the Workflow Engine world meet.
A farmer's planted Crop record (crop_type, sowing_date) lives in the
database; app.engines.workflow only knows about crop *types* and dates
and has never heard of a Farmer, Field, or database session.

Route responsibility: fetch the Crop row, translate it into the two
plain values the engine needs (crop_type, sowing_date), call the engine,
and translate the engine's typed exceptions into HTTP responses.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.engines.workflow import get_daily_workflow
from app.engines.workflow.crop_loader import CropLoadError, CropNotFoundError
from app.engines.workflow.guideline_loader import GuidelineNotFoundError
from app.engines.workflow.stage_resolver import StageNotFoundError
from app.schemas.workflow import WorkflowStatusResponse
from app.services.crop_service import CropService

router = APIRouter(prefix="/crops", tags=["Crop Workflow"])


@router.get(
    "/{crop_id}/workflow-status",
    response_model=WorkflowStatusResponse,
    summary="Get today's growth-stage guidance for a planted crop",
)
def get_workflow_status(
    crop_id: UUID,
    as_of: Optional[date] = Query(
        default=None,
        description=(
            "Calculate guidance as of this date instead of today. "
            "Useful for testing or reviewing what guidance looked like "
            "on a past date."
        ),
    ),
    db: Session = Depends(get_db),
) -> WorkflowStatusResponse:
    """
    Resolve the current growth stage for a farmer's planted crop and
    return the matching irrigation, fertilizer, pest, and disease guidance.

    Flow:
        Crop DB record (by crop_id)
        -> crop.crop_type + crop.sowing_date
        -> Workflow Engine (get_daily_workflow)
        -> current stage + full guidance payload

    Path params:
        crop_id: UUID of the planted Crop record (NOT the knowledge base
                 crop key like "rice" — that's derived internally from
                 crop.crop_type).

    Query params:
        as_of: optional date override, defaults to today.

    Raises:
        404: Crop record doesn't exist, or its crop_type has no matching
             knowledge base file (e.g. "wheat" before wheat.json exists).
        400: Crop record exists but has no sowing_date recorded.
        422: The crop's calculated days-after-sowing falls outside every
             defined growth stage — most commonly because it's overdue
             for harvest.
        500: The knowledge base file for this crop is corrupted, or
             growth_timeline and stage_guidelines have gotten out of
             sync (a data bug, not something the caller can fix).
    """
    crop = CropService.get_crop_by_id(db, crop_id)
    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop record '{crop_id}' not found.",
        )

    if not crop.sowing_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Crop '{crop_id}' has no sowing_date recorded — "
                f"cannot calculate growth stage."
            ),
        )

    try:
        result = get_daily_workflow(
            crop_id=crop.crop_type,
            sowing_date=crop.sowing_date,
            today=as_of,
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

    return result