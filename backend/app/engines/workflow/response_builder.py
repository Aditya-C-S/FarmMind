"""
Response Builder
----------------
Assembles the final structured response returned by the Workflow Engine —
the shape the Dashboard consumes today, and that the Context Fusion Engine
will consume later without needing to know about stage_calculator,
crop_loader, stage_resolver, or guideline_loader at all.
"""

from typing import Any, Dict


def build_response(
    crop_id: str,
    das_info: Dict[str, Any],
    guideline: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the final workflow response.

    Args:
        crop_id: e.g. "rice" (from crop_data["crop_id"], not the raw input
                 string, so casing/aliasing is normalized)
        das_info: output of stage_resolver.resolve_stage()
        guideline: output of guideline_loader.load_guidelines()

    Returns:
        {
            "crop_id": "rice",
            "current_day": 38,
            "current_stage": {"stage_id", "stage", "day_start", "day_end"},
            "next_stage": {same shape} | None,
            "days_remaining_in_stage": 7,
            "guidance": {
                "objective": str,
                "description": str,
                "tasks": [...],
                "irrigation": {...},
                "fertilizer": {...},
                "weed_management": {...},
                "monitoring": [...],
                "pest_alerts": [...],       # full pest objects + risk_level
                "disease_alerts": [...],    # full disease objects + risk_level
                "best_practices": [...],
                "expected_crop_status": [...]
            }
        }
    """
    return {
        "crop_id": crop_id,
        "current_day": das_info["current_day"],
        "current_stage": das_info["current_stage"],
        "next_stage": das_info["next_stage"],
        "days_remaining_in_stage": das_info["days_remaining"],
        "guidance": {
            "objective": guideline.get("objective"),
            "description": guideline.get("description"),
            "tasks": guideline.get("tasks", []),
            "irrigation": guideline.get("irrigation", {}),
            "fertilizer": guideline.get("fertilizer", {}),
            "weed_management": guideline.get("weed_management", {}),
            "monitoring": guideline.get("monitoring", []),
            "pest_alerts": guideline.get("common_pests", []),
            "disease_alerts": guideline.get("common_diseases", []),
            "best_practices": guideline.get("best_practices", []),
            "expected_crop_status": guideline.get("expected_crop_status", []),
            # Harvest-stage fields — present only when stage_id == "harvest",
            # None/absent for all other stages (frontend checks before rendering)
            "maturity_indicators": guideline.get("maturity_indicators", []),
            "harvest_methods": guideline.get("harvest_methods", []),
            "post_harvest": guideline.get("post_harvest"),
            "spoilage_checks": guideline.get("spoilage_checks"),
        },
    }