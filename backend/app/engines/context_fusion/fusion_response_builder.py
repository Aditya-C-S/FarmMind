"""
Fusion Response Builder
-----------------------
Assembles the final merged response: Workflow Engine's expected picture +
real weather + real logged activity + (optionally) real disease detection.
"""

from typing import Any, Dict


def build_fusion_response(
    workflow_result: Dict[str, Any],
    weather_context: Dict[str, Any],
    activity_context: Dict[str, Any],
    disease_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Args:
        workflow_result: output of app.engines.workflow.get_daily_workflow()
        weather_context: output of weather_context.get_weather_context()
        activity_context: output of activity_context.get_activity_context()
        disease_context: output of disease_context.get_disease_context()

    Returns:
        {
            "crop_id": ...,
            "current_stage": {...},
            "next_stage": {...} | None,
            "days_remaining_in_stage": int,
            "guidance": {...},          # unchanged from the Workflow Engine
            "weather_context": {...},
            "activity_context": {...},
            "disease_context": {...},
        }
    """
    return {
        "crop_id": workflow_result["crop_id"],
        "current_stage": workflow_result["current_stage"],
        "next_stage": workflow_result["next_stage"],
        "days_remaining_in_stage": workflow_result["days_remaining_in_stage"],
        "guidance": {"workflow": workflow_result["guidance"], "disease_prevention": weather_context.get("prevention", []),"irrigation": weather_context.get("irrigation")},
        "weather_context": weather_context,
        "activity_context": activity_context,
        "disease_context": disease_context,
    }