"""
Activity Context
-----------------
Compares the Workflow Engine's recommended tasks for the current stage
(free-text strings like "Control weeds.") against the farmer's actual
logged activities (ActivityLog, Phase 2) to flag each task as done,
pending, or overdue.

IMPORTANT — known limitation, flagged deliberately rather than hidden:
`ActivityLog.activity_type` is currently a free-text string with no
enforced vocabulary (confirmed — there's no enum in the schema). That
means there's no reliable field to match "Control weeds." against; the
best available signal is keyword overlap between the recommended task
text and the logged activity_type/description text. This is a heuristic,
not an exact match, and will miss activities logged with unrelated
wording (e.g. "sprayed field" for a weeding task).

Recommended fix, whenever it's convenient (doesn't require a migration
of old data): agree on a small controlled vocabulary for activity_type
going forward — e.g. "irrigation", "weeding", "fertilizer_application",
"pest_control", "monitoring", "spraying", "other" — and this module can
switch from keyword matching to an exact lookup table, which will be far
more reliable. Until then, keyword matching is the pragmatic MVP option.
"""

from datetime import date, timedelta
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.activity_service import ActivityService

# Task keyword -> activity_type/description keywords considered a match.
# Extend this table as more task phrasing shows up across crops.
_TASK_KEYWORD_MAP: Dict[str, List[str]] = {
    "irrigat": ["irrigat", "water"],
    "weed": ["weed"],
    "fertiliz": ["fertiliz", "fertilis", "nutrient", "top-dress", "top dress"],
    "monitor": ["monitor", "scout", "inspect"],
    "pest": ["pest", "spray", "insecticide"],
    "diseas": ["disease", "fungicide"],
    "harvest": ["harvest"],
}

# How far back to look for a matching logged activity before calling a task "overdue"
_LOOKBACK_DAYS = 7


def _task_keywords(task_text: str) -> List[str]:
    """Find which keyword group(s) a recommended task text belongs to."""
    lowered = task_text.lower()
    matched = []
    for group_key, variants in _TASK_KEYWORD_MAP.items():
        if any(v in lowered for v in variants):
            matched.append(group_key)
    return matched


def _activity_matches_group(activity: Any, group_key: str) -> bool:
    variants = _TASK_KEYWORD_MAP[group_key]
    haystack = f"{activity.activity_type or ''} {activity.description or ''}".lower()
    return any(v in haystack for v in variants)


def get_activity_context(
    db: Session,
    crop_id: UUID,
    recommended_tasks: List[str],
    as_of: date = None,
) -> Dict[str, Any]:
    """
    Check each recommended task against recently logged activities.

    Args:
        db: SQLAlchemy session
        crop_id: the planted crop's UUID
        recommended_tasks: guidance.tasks from the Workflow Engine's response
        as_of: reference date for the lookback window; defaults to today

    Returns:
        {
            "lookback_days": 7,
            "task_status": [
                {"task": "Control weeds.", "status": "done" | "pending", "matched_activity_date": date | None},
                ...
            ]
        }

    Note: "pending" is used rather than "overdue" deliberately — with only
    keyword matching available, confidently declaring a task overdue (as
    opposed to just not yet matched) risks false alarms. Use "pending" as
    a prompt for the farmer to confirm, not a hard failure.
    """
    reference_date = as_of or date.today()
    window_start = reference_date - timedelta(days=_LOOKBACK_DAYS)

    recent_activities = ActivityService.get_activities_by_date_range(
        db, crop_id, window_start, reference_date
    )

    task_status = []
    for task in recommended_tasks:
        groups = _task_keywords(task)
        matched_date = None

        if groups:
            for activity in recent_activities:
                if any(_activity_matches_group(activity, g) for g in groups):
                    matched_date = activity.activity_date
                    break

        task_status.append(
            {
                "task": task,
                "status": "done" if matched_date else "pending",
                "matched_activity_date": matched_date,
            }
        )

    return {
        "lookback_days": _LOOKBACK_DAYS,
        "task_status": task_status,
    }