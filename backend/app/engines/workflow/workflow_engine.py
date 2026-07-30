"""
Workflow Engine
---------------
Top-level orchestrator for the flow:

    Farmer opens app
        -> Workflow Engine
            -> Load crop            (crop_loader)
            -> Calculate DAS        (stage_calculator)
            -> Find stage           (stage_resolver)
            -> Load guidelines      (guideline_loader)
            -> Return response      (response_builder)
        -> Dashboard

This is the only module the rest of the app (API routes, Context Fusion
Engine later) should need to import. Everything else in this package is
an internal implementation detail reachable through here.
"""

from datetime import date
from typing import Any, Dict, Union

from . import crop_loader, guideline_loader, response_builder, stage_calculator, stage_resolver

DateLike = Union[date, str]


def get_daily_workflow(
    crop_id: str,
    sowing_date: DateLike,
    today: DateLike = None,
) -> Dict[str, Any]:
    """
    Return today's workflow guidance for a given crop planting.

    Args:
        crop_id: e.g. "rice", "tomato" — must match a file in app/knowledge/
        sowing_date: date the crop was sown/planted (date object or ISO string)
        today: reference date to calculate against; defaults to the actual
               current date. Exposed mainly for testing and for backfilling
               guidance on past dates.

    Returns:
        The structured response from response_builder.build_response() —
        current stage, next stage, days remaining, and full stage guidance
        including expanded pest/disease alerts.

    Raises:
        crop_loader.CropNotFoundError: crop_id has no knowledge base file
        crop_loader.CropLoadError: the knowledge base file has invalid JSON
        stage_resolver.StageNotFoundError: DAS falls outside every defined
            stage (e.g. crop is overdue for harvest, or timeline data is
            incomplete)
        guideline_loader.GuidelineNotFoundError: growth_timeline and
            stage_guidelines are out of sync in the knowledge base (data bug)
    """
    crop_data = crop_loader.load_crop(crop_id)

    das = stage_calculator.calculate_das(sowing_date, today)

    das_info = stage_resolver.resolve_stage(crop_data, das)

    stage_id = das_info["current_stage"]["stage_id"]
    guideline = guideline_loader.load_guidelines(crop_data, stage_id)

    return response_builder.build_response(
        crop_id=crop_data.get("crop_id", crop_id),
        das_info=das_info,
        guideline=guideline,
    )