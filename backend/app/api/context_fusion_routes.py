"""
Context Fusion Routes
----------------------
POST /crops/{crop_id}/context-status

Same bridging role as workflow_routes.py, one level up: fetches the Crop
record, pulls crop_type/sowing_date/field_id from it, and calls the
Context Fusion Engine — which itself calls the Workflow Engine plus real
weather and activity data. Disease detections are accepted in the request
body rather than computed here, since this route never calls Aditya's
pipeline directly (see context_fusion_engine.py for why).
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.engines.context_fusion import get_fused_context
from app.engines.workflow.crop_loader import CropLoadError, CropNotFoundError
from app.engines.workflow.guideline_loader import GuidelineNotFoundError
from app.engines.workflow.stage_resolver import StageNotFoundError
from app.models.field import Field
from app.schemas.context_fusion import ContextFusionRequest, ContextFusionResponse
from app.services.crop_service import CropService

router = APIRouter(prefix="/crops", tags=["Context Fusion"])


@router.post(
    "/{crop_id}/context-status",
    response_model=ContextFusionResponse,
    summary="Get the fully merged context for a planted crop",
)
def get_context_status(
    crop_id: UUID,
    request: ContextFusionRequest = ContextFusionRequest(),
    as_of: Optional[date] = Query(
        default=None,
        description="Calculate context as of this date instead of today.",
    ),
    db: Session = Depends(get_db),
) -> ContextFusionResponse:
    """
    Resolve the current growth stage (via the Workflow Engine) and merge
    it with real weather, real logged farmer activity, and any disease
    detection results supplied in the request body.

    Flow:
        Crop DB record (by crop_id)
        -> crop.crop_type + crop.sowing_date + crop.field_id
        -> Context Fusion Engine
        -> merged stage + weather + activity + disease picture

    Body:
        detections: list of run_pipeline()-shaped dicts. Omit or send an
                    empty list if no photo has been analyzed for this crop
                    yet — the response will simply show every expected
                    disease risk as "expected_unconfirmed".

    Query params:
        as_of: optional date override, defaults to today.

    Raises:
        404: Crop record doesn't exist, or its crop_type has no matching
             knowledge base file.
        400: Crop record exists but has no sowing_date recorded.
        422: The crop's days-after-sowing falls outside every defined
             growth stage (most commonly: overdue for harvest).
        500: Knowledge base file is corrupted, or growth_timeline and
             stage_guidelines are out of sync (a data bug).
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

    # Field coordinates are needed for the live Open-Meteo weather lookup.
    # Missing coordinates aren't fatal — weather_context.py degrades
    # gracefully (data_available=False) rather than this route failing
    # the whole request over it.
    field = db.query(Field).filter(Field.field_id == crop.field_id).first()
    latitude = field.latitude if field else None
    longitude = field.longitude if field else None

    try:
        result = get_fused_context(
            db=db,
            crop_id=crop.crop_id,
            latitude=latitude,
            longitude=longitude,
            crop_type=crop.crop_type,
            sowing_date=crop.sowing_date,
            detections=[d.model_dump() for d in request.detections],
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

    return result