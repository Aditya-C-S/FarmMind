"""
app/engines/decision_optimization/alternative_builder.py

Alternative Builder — turns an already-fused context (weather + disease +
activity, i.e. the output of `get_fused_context()`) into a flat list of
candidate actions, ready to hand to AHP + TOPSIS.

This intentionally replaces the "Task Generation Engine" step in the fuller
pipeline design for now. It is a pure function of its input: no DB access,
no network calls, no teammate imports — same "take their output shape as a
parameter" principle Context Fusion already follows.
"""

from typing import Any, Optional


# ---------------------------------------------------------------------------
# Heuristic tables — tune freely, these are starting points not physics.
# ---------------------------------------------------------------------------

RISK_LEVEL_SCORES = {
    "low": 0.3,
    "medium": 0.6,
    "moderate": 0.6,
    "high": 0.9,
    "severe": 0.95,
    "critical": 1.0,
}

# Same keyword-matching idiom activity_context.py already uses for
# activity_type — kept consistent rather than inventing a new approach.
EFFORT_KEYWORDS = [
    ("spray", 0.7),
    ("pesticide", 0.7),
    ("fungicide", 0.7),
    ("herbicide", 0.6),
    ("irrigat", 0.3),
    ("water", 0.3),
    ("weed", 0.5),
    ("fertiliz", 0.4),
    ("prune", 0.5),
    ("harvest", 0.8),
    ("scout", 0.2),
    ("inspect", 0.2),
    ("monitor", 0.2),
]
DEFAULT_EFFORT = 0.4

WEATHER_ACTION_MAP = {
    "high_humidity": {
        "task": "Inspect crop for fungal disease — humidity is elevated",
        "urgency": 0.5,
        "risk": 0.5,
        "effort": 0.3,
    },
    "heavy_rainfall": {
        "task": "Check field drainage and waterlogging",
        "urgency": 0.7,
        "risk": 0.6,
        "effort": 0.4,
    },
    "high_temperature": {
        "task": "Increase irrigation frequency — heat stress risk",
        "urgency": 0.6,
        "risk": 0.4,
        "effort": 0.5,
    },
    "drought": {
        "task": "Schedule irrigation — prolonged dry spell detected",
        "urgency": 0.8,
        "risk": 0.7,
        "effort": 0.6,
    },
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _dig(obj: Any, *key_groups: list) -> Any:
    """
    Try several possible nesting paths and return the first hit.
    Each entry in key_groups is itself a list of keys to walk in sequence.
    Mirrors the .get()-with-defaults defensiveness already used elsewhere
    in this codebase (fertilizer shape, stage display name fallback, etc).
    """
    for path in key_groups:
        cur = obj
        ok = True
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


def _risk_from_level(level: Optional[str], default: float = 0.5) -> float:
    if not level:
        return default
    return RISK_LEVEL_SCORES.get(str(level).strip().lower(), default)


def _effort_for(text: str) -> float:
    lowered = (text or "").lower()
    for keyword, score in EFFORT_KEYWORDS:
        if keyword in lowered:
            return score
    return DEFAULT_EFFORT


def _disease_label(item: dict) -> str:
    return (
        item.get("disease")
        or item.get("disease_id")
        or item.get("name")
        or item.get("label")
        or "unknown disease"
    )


def _economic_loss(item: dict) -> float:
    """
    Prefer loss_if_delayed — it represents the cost of NOT acting, which is
    what should drive this action's priority. Falls back through the other
    economic_loss fields, then 0 if no detection-derived figures exist.
    """
    loss_block = item.get("economic_loss") or {}
    for key in ("loss_if_delayed", "loss_if_act_now", "extra_loss_from_delay"):
        val = loss_block.get(key)
        if isinstance(val, (int, float)):
            return float(val)
    return 0.0


# ---------------------------------------------------------------------------
# Per-source builders
# ---------------------------------------------------------------------------

def _from_disease_buckets(fused_context: dict) -> list[dict]:
    alternatives = []

    disease_block = _dig(
        fused_context,
        ["disease_context"],
        ["disease"],
        [],  # fall back to treating fused_context itself as the disease block
    ) or fused_context

    confirmed = disease_block.get("confirmed") or []
    unexpected = disease_block.get("unexpected_detections") or []
    expected_unconfirmed = disease_block.get("expected_unconfirmed") or []
    unmapped = disease_block.get("unmapped_detections") or []

    for item in confirmed:
        label = _disease_label(item)
        risk = _risk_from_level(item.get("severity_class") or item.get("risk_level"))
        worsening = str(item.get("progression", "")).lower() == "worsening"
        urgency = min(1.0, risk + (0.1 if worsening else 0.0))
        task = f"Treat {label} — confirmed by detection and expected at this stage"
        alternatives.append({
            "task": task,
            "urgency": round(urgency, 2),
            "risk": round(risk, 2),
            "loss": _economic_loss(item),
            "effort": _effort_for(task),
            "source": "disease_confirmed",
        })

    for item in unexpected:
        label = _disease_label(item)
        risk = _risk_from_level(item.get("severity_class") or item.get("risk_level"), default=0.5)
        task = f"Investigate unexpected {label} detection — not typical for this stage"
        alternatives.append({
            "task": task,
            "urgency": round(risk * 0.8, 2),
            "risk": round(risk, 2),
            "loss": _economic_loss(item),
            "effort": _effort_for(task),
            "source": "disease_unexpected",
        })

    for item in expected_unconfirmed:
        label = _disease_label(item)
        risk = _risk_from_level(item.get("risk_level"), default=0.4)
        task = f"Scout for {label} (expected this stage)"
        alternatives.append({
            "task": task,
            "urgency": 0.3,
            "risk": round(risk, 2),
            "loss": 0.0,
            "effort": _effort_for("scout"),
            "source": "disease_expected_unconfirmed",
        })

    for item in unmapped:
        label = item.get("disease") or item.get("label") or "unrecognized label"
        task = f"Manual review: detection '{label}' is outside current MVP disease scope"
        alternatives.append({
            "task": task,
            "urgency": 0.4,
            "risk": 0.5,
            "loss": 0.0,
            "effort": 0.3,
            "source": "disease_unmapped",
        })

    return alternatives


def _from_weather(fused_context: dict) -> list[dict]:
    weather = _dig(fused_context, ["weather_context"], ["weather"]) or {}

    if not weather.get("data_available", False):
        return []  # no coordinates / network failure — nothing to act on

    # Retrieve triggered alerts from the true weather_context output shape
    alerts = _dig(weather, ["triggered_alerts"], ["alerts"], ["triggers"], ["flags"]) or []
    
    triggers = []
    for alert in alerts:
        if isinstance(alert, dict) and "weather_id" in alert:
            triggers.append(alert["weather_id"])
        elif isinstance(alert, str):
            triggers.append(alert)

    alternatives = []
    for trigger in triggers:
        template = WEATHER_ACTION_MAP.get(trigger)
        if not template:
            continue
        alternatives.append({
            "task": template["task"],
            "urgency": template["urgency"],
            "risk": template["risk"],
            "loss": 0.0,  # no economic model tied to weather triggers yet
            "effort": template["effort"],
            "source": "weather",
        })
    
    irrigation = weather.get("irrigation")
    if irrigation:
        status = irrigation.get("status", "").lower()
        if status == "attention":
            urgency = 0.9
            risk = 0.8
        elif status == "required":
            urgency = 0.7
            risk = 0.6
        elif status == "moderate":
            urgency = 0.5
            risk = 0.4
        else:   # Good
            urgency = 0.3
            risk = 0.2
        alternatives.append({
            "task": irrigation["level"],
            "urgency": urgency,
            "risk": risk,
            "loss": 0.0,
            "effort": 0.3,
            "source": "weather_irrigation",
            "reason": irrigation.get("reason", ""),
        })
    prevention = weather.get("prevention", [])

    for disease in prevention:

        risk_level = disease["risk"].lower()

        if risk_level == "high":
            urgency = 0.9
            risk = 0.9
        elif risk_level == "medium":
            urgency = 0.6
            risk = 0.6
        else:
            urgency = 0.3
            risk = 0.3

        for recommendation in disease["recommendations"]:

            alternatives.append({
                "task": recommendation,
                "urgency": urgency,
                "risk": risk,
                "loss": 0.0,
                "effort": 0.2,
                "source": "weather_prevention",
                "reason": disease["reason"],
                "disease": disease["disease"],
            })

    return alternatives


def _from_workflow_pending(fused_context: dict, workflow: Optional[dict] = None) -> list[dict]:
    """
    Looks for a list of task statuses that carry a status flag.
    Tries the fused context's activity_context first, then an
    optionally-supplied raw workflow response as a fallback source of task
    text.
    """
    alternatives = []

    pending_source = _dig(
        fused_context,
        ["activity_context", "task_status"],
        ["activity", "pending_tasks"],
        ["activity_context", "pending_tasks"],
        ["pending_tasks"],
    )

    if pending_source is None and workflow is not None:
        # Fall back to raw recommended actions from the workflow response,
        # with no completion info — treat everything as pending.
        pending_source = _dig(
            workflow,
            ["guidance", "tasks"],
            ["recommended_actions"],
            ["current_stage", "recommended_actions"],
            ["current_stage", "tasks"],
        ) or []

    for entry in pending_source or []:
        # entry might be a dict like {"task": "...", "status": "pending"} or a string
        if isinstance(entry, dict):
            status = entry.get("status")
            if status == "done" or entry.get("completed"):
                continue
            task_text = entry.get("task") or entry.get("description") or str(entry)
        else:
            task_text = str(entry)

        alternatives.append({
            "task": task_text,
            "urgency": 0.4,
            "risk": 0.4,
            "loss": 0.0,
            "effort": _effort_for(task_text),
            "source": "workflow_pending",
        })

    return alternatives


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_alternatives(fused_context: dict, workflow: Optional[dict] = None) -> list[dict]:
    """
    fused_context: the dict returned by get_fused_context() (Phase 4 output).
    workflow: optional raw get_daily_workflow() response, used only as a
        fallback source of pending task text if fused_context doesn't
        already embed it.

    Returns a flat list of candidate action dicts:
        {"task", "urgency", "risk", "loss", "effort", "source"}
    "loss" is left in raw currency units (or 0.0) on purpose — normalizing
    across alternatives is TOPSIS's job, not this module's.
    """
    alternatives: list[dict] = []
    alternatives.extend(_from_disease_buckets(fused_context))
    alternatives.extend(_from_weather(fused_context))
    alternatives.extend(_from_workflow_pending(fused_context, workflow))
    return alternatives


# ---------------------------------------------------------------------------
# Standalone smoke test — run `python alternative_builder.py` to sanity-check
# the logic against a synthetic fused_context before wiring it into FastAPI.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    sample_fused_context = {
        "weather_context": {
            "data_available": True,
            "triggered_alerts": [
                {"weather_id": "high_humidity"}, 
                {"weather_id": "drought"}
            ],
        },
        "disease_context": {
            "confirmed": [
                {
                    "disease": "TYLCV",
                    "severity_class": "Moderate",
                    "progression": "Worsening",
                    "economic_loss": {
                        "loss_if_act_now": 12450.0,
                        "loss_if_delayed": 21830.0,
                        "delay_days": 7,
                        "extra_loss_from_delay": 9380.0,
                    },
                }
            ],
            "unexpected_detections": [],
            "expected_unconfirmed": [
                {"disease": "sheath_blight", "risk_level": "Medium"}
            ],
            "unmapped_detections": [],
        },
        "activity_context": {
            "task_status": [
                {"task": "Control weeds.", "status": "pending"},
                {"task": "Apply basal fertilizer.", "status": "done"},
            ]
        },
    }

    result = build_alternatives(sample_fused_context)
    print(json.dumps(result, indent=2))
