"""
Stage Resolver
--------------
Given a crop's knowledge base and a DAS value, finds the current growth
stage AND the next one, returning full stage metadata rather than just
a stage_id or name.

This is the design choice from the review: by returning the complete
stage objects here, GuidelineLoader never has to re-search
growth_timeline — it already knows exactly which stage_id to look up
in stage_guidelines. Single search, not two.
"""

from typing import Any, Dict, Optional


class StageNotFoundError(Exception):
    """Raised when a DAS value doesn't fall within any defined stage range."""


def _with_display_name(stage: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarantee a human-readable "stage" name is present.

    Not every knowledge base file populates growth_timeline.stages[i]["stage"]
    (rice.json does; tomato.json currently doesn't — confirmed by testing,
    not just schema review). Rather than let that inconsistency propagate
    into the API response and dashboard, derive a readable fallback from
    stage_id (e.g. "panicle_initiation" -> "Panicle Initiation") when it's
    missing. Returns a shallow copy — never mutates the cached crop_data.
    """
    if stage.get("stage"):
        return stage
    enriched = dict(stage)
    enriched["stage"] = stage["stage_id"].replace("_", " ").title()
    return enriched


def resolve_stage(crop_data: Dict[str, Any], das: int) -> Dict[str, Any]:
    """
    Resolve the current and next growth stage for a given DAS.

    Args:
        crop_data: full crop knowledge base, as returned by crop_loader.load_crop()
        das: Days After Sowing (from stage_calculator.calculate_das())

    Returns:
        {
            "current_stage": {"stage_id": ..., "stage": ..., "day_start": ..., "day_end": ...},
            "next_stage": {same shape} or None if current stage is the last one,
            "current_day": das,
            "days_remaining": int,  # days left until current_stage.day_end (>= 0)
        }

    Raises:
        StageNotFoundError: if das falls outside every stage's day range —
            e.g. das exceeds the crop's total defined duration (harvest
            overdue) or growth_timeline data is incomplete.
    """
    stages = crop_data.get("growth_timeline", {}).get("stages", [])
    if not stages:
        raise StageNotFoundError(
            f"'{crop_data.get('crop_id', 'unknown crop')}' has no stages "
            f"defined in growth_timeline.stages"
        )

    # Sort defensively by day_start — don't assume JSON authoring order is correct
    ordered_stages = sorted(stages, key=lambda s: s["day_start"])

    current_index: Optional[int] = None
    for i, stage in enumerate(ordered_stages):
        if stage["day_start"] <= das <= stage["day_end"]:
            current_index = i
            break

    if current_index is None:
        last_stage = ordered_stages[-1]
        if das > last_stage["day_end"]:
            raise StageNotFoundError(
                f"DAS {das} exceeds the last defined stage "
                f"('{last_stage['stage_id']}', ends day {last_stage['day_end']}). "
                f"Crop may be overdue for harvest, or growth_timeline data is incomplete."
            )
        raise StageNotFoundError(f"DAS {das} does not fall within any defined stage range.")

    current_stage = _with_display_name(ordered_stages[current_index])
    next_stage = (
        _with_display_name(ordered_stages[current_index + 1])
        if current_index + 1 < len(ordered_stages)
        else None
    )

    days_remaining = max(current_stage["day_end"] - das, 0)

    return {
        "current_stage": current_stage,
        "next_stage": next_stage,
        "current_day": das,
        "days_remaining": days_remaining,
    }