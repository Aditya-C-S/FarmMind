"""
Post-Harvest Intelligence Engine.

Pipeline:
  harvest_record + latest condition log + knowledge base
        │
        ├── shelf_life_assessment()   → remaining days, % consumed
        ├── condition_assessment()    → risk score from temp/humidity/visual
        └── recommendation_builder() → ordered action list

No ML. All decisions are threshold comparisons against KB-sourced rules.
"""

import logging
from typing import Optional

from app.engines.post_harvest.rules import (
    SHELF_LIFE_DAYS,
    OPTIMAL_CONDITIONS,
    VISUAL_RISK_WEIGHT,
    score_to_spoilage_risk,
    score_to_storage_health,
)
from app.engines.workflow.crop_loader import load_crop

from app.services.storage_recommendations import (
    get_storage_recommendation,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def get_post_harvest_assessment(
    crop_type: str,
    storage_type: str,
    days_in_storage: int,
    quantity_kg: float,
    harvest_id,
    latest_log: Optional[dict] = None,
) -> dict:
    """
    Produce a full post-harvest assessment for one harvest record.

    Args:
        crop_type:       e.g. "rice" or "tomato" (will be lowercased)
        storage_type:    one of cold_room | ambient | covered_shed | open
        days_in_storage: days since harvest_date (pre-computed by route layer)
        quantity_kg:     harvested quantity
        harvest_id:      UUID (passed through to response, not used in logic)
        latest_log:      dict matching StorageConditionLog.to_dict(), or None

    Returns:
        dict matching PostHarvestAssessment schema
    """
    crop_key = crop_type.lower()

    # ── Shelf Life ─────────────────────────────────────────────────────────
    shelf = _shelf_life_assessment(crop_key, storage_type, days_in_storage)

    # ── Condition Assessment ────────────────────────────────────────────────
    condition = _condition_assessment(crop_key, storage_type, latest_log)

    # ── Factor in shelf life consumption as a risk contributor ────────────
    # If >80% of shelf life is consumed, bump risk by 1 point regardless of
    # current conditions — the clock is the primary spoilage driver for perishables.
    shelf_pct = shelf["shelf_life_consumed_percent"]
    if shelf_pct >= 100:
        condition["risk_score"] += 3   # Past shelf life → critical
        condition["risk_factors"].insert(0, "Estimated shelf life has been exceeded.")
    elif shelf_pct >= 80:
        condition["risk_score"] += 1
        condition["risk_factors"].insert(0, f"Shelf life {shelf_pct:.0f}% consumed — sell or move to better storage soon.")
    elif shelf_pct >= 60:
        condition["risk_factors"].append(f"Shelf life {shelf_pct:.0f}% consumed — monitor closely.")

    # ── Derive status labels ────────────────────────────────────────────────
    spoilage_risk = score_to_spoilage_risk(condition["risk_score"])

    storage_health = {
        "overall_status": score_to_storage_health(condition["risk_score"]),
        "temperature_ok": condition["temperature_ok"],
        "humidity_ok": condition["humidity_ok"],
        "moisture_ok": condition["moisture_ok"],
        "out_of_range_params": condition["out_of_range_params"],
    }

    # Normalized 0–1 score for frontend progress indicators.
    # Max meaningful risk_score is ~5 (1 temp + 1 humidity + 1 visual weight
    # + 1 open storage + 1 shelf-life bump), so dividing by 5 gives a clean
    # 0–1 range without ever exceeding it in normal operation.
    spoilage_risk_score = min(condition["risk_score"] / 5.0, 1.0)

    # ── Knowledge Base best practices ──────────────────────────────────────
    best_practices = _get_kb_best_practices(crop_key)
    recommendation = get_storage_recommendation(crop_key,storage_type,)

    # ── Recommendations ────────────────────────────────────────────────────
    storage_health_status = storage_health["overall_status"]

    recommendations = _build_recommendations(
        crop_key=crop_key,
        storage_type=storage_type,
        spoilage_risk=spoilage_risk,
        storage_health=storage_health_status,
        risk_factors=condition["risk_factors"],
        shelf_pct=shelf_pct,
        latest_log=latest_log,
    )

    # ── Human summaries ────────────────────────────────────────────────────
    health_summary = _health_summary(storage_health_status, days_in_storage, crop_key)
    spoilage_summary = _spoilage_summary(spoilage_risk, shelf, crop_key)

    return {
        "harvest_id": harvest_id,
        "crop_type": crop_type,
        "storage_type": storage_type,
        "days_in_storage": days_in_storage,
        "quantity_kg": quantity_kg,
        **shelf,
        "storage_health": storage_health,
        "spoilage_risk_level": spoilage_risk,
        "spoilage_risk_score": round(spoilage_risk_score, 3),
        "spoilage_risk": spoilage_risk,  # kept for backwards compatibility
        "health_summary": health_summary,
        "spoilage_summary": spoilage_summary,
        "spoilage_signs_to_watch": condition["risk_factors"],
        "ranked_actions": recommendations,
        "latest_log": latest_log,
        "best_practices": best_practices,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _shelf_life_assessment(crop_key: str, storage_type: str, days_in_storage: int) -> dict:
    """Compute shelf life metrics from rule table."""
    crop_shelf = SHELF_LIFE_DAYS.get(crop_key, SHELF_LIFE_DAYS["rice"])
    total_days = crop_shelf.get(storage_type, crop_shelf.get("ambient", 90))

    remaining = max(0, total_days - days_in_storage)
    consumed_pct = min(100.0, round((days_in_storage / total_days) * 100, 1))
    remaining_pct = max(0.0, round(100 - consumed_pct, 1))

    return {
        "base_shelf_life_days": total_days,
        "remaining_shelf_life_days": remaining,
        "shelf_life_consumed_percent": consumed_pct,   # used internally by risk bump logic
        "shelf_life_pct_remaining": remaining_pct,     # exposed to frontend — was returning consumed by mistake
    }


def _condition_assessment(
    crop_key: str, storage_type: str, log: Optional[dict]
) -> dict:
    """
    Score current storage conditions against KB-sourced thresholds.
    Each out-of-range condition adds 1 point; visual condition adds its weight.
    """
    risk_score = 0
    risk_factors = []
    out_of_range = []

    if log is None:
        return {
            "risk_score": 0,
            "risk_factors": ["No condition log recorded yet — conditions unverified."],
            "temperature_ok": None,
            "humidity_ok": None,
            "moisture_ok": None,
            "out_of_range_params": [],
        }

    optimal = OPTIMAL_CONDITIONS.get(crop_key, OPTIMAL_CONDITIONS["rice"])
    temp = log.get("temperature_c")
    humidity = log.get("humidity_percent")
    visual = log.get("visual_condition", "good")

    # Temperature check
    temperature_ok = None
    if temp is not None:
        temperature_ok = True
        if optimal.get("temp_max_c") is not None and temp > optimal["temp_max_c"]:
            risk_score += 1
            temperature_ok = False
            out_of_range.append("temperature")
            risk_factors.append(
                f"Temperature {temp}°C exceeds safe maximum of {optimal['temp_max_c']}°C."
            )
        elif optimal.get("temp_min_c") is not None and temp < optimal["temp_min_c"]:
            risk_score += 1
            temperature_ok = False
            out_of_range.append("temperature")
            risk_factors.append(
                f"Temperature {temp}°C is below recommended minimum of {optimal['temp_min_c']}°C."
            )

    # Humidity check
    humidity_ok = None
    if humidity is not None:
        humidity_ok = True
        if optimal.get("humidity_max") is not None and humidity > optimal["humidity_max"]:
            risk_score += 1
            humidity_ok = False
            out_of_range.append("humidity")
            risk_factors.append(
                f"Humidity {humidity}% exceeds safe maximum of {optimal['humidity_max']}%."
            )
        elif optimal.get("humidity_min") is not None and humidity < optimal["humidity_min"]:
            risk_score += 1
            humidity_ok = False
            out_of_range.append("humidity")
            risk_factors.append(
                f"Humidity {humidity}% is below recommended minimum of {optimal['humidity_min']}%."
            )

    # Moisture — not in StorageConditionLog yet, placeholder for future
    moisture_ok = None  # set to True/False once moisture_percent field exists

    # Visual condition
    visual_weight = VISUAL_RISK_WEIGHT.get(visual, 0)
    risk_score += visual_weight
    if visual == "early_spoilage":
        risk_factors.append("Visual inspection shows early signs of spoilage.")
    elif visual == "critical":
        risk_factors.append("Visual inspection shows critical spoilage — immediate action required.")

    # Storage type suitability warning
    if storage_type == "open":
        risk_score += 1
        risk_factors.append("Open storage offers no protection from moisture, pests, or weather.")

    return {
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "temperature_ok": temperature_ok,
        "humidity_ok": humidity_ok,
        "moisture_ok": moisture_ok,
        "out_of_range_params": out_of_range,
    }


def _get_kb_best_practices(crop_key: str) -> list[str]:
    """Pull storage best practices directly from the knowledge base."""
    try:
        kb = load_crop(crop_key)
        storage = kb.get("post_harvest", {}).get("storage", {})
        practices = (
            storage.get("recommended_practices", [])
            + storage.get("safe_storage_conditions", [])
            + storage.get("good_storage_practices", [])
        )
        return practices if practices else _fallback_practices(crop_key)
    except Exception:
        logger.warning(f"Could not load KB for {crop_key} — using fallback practices.")
        return _fallback_practices(crop_key)


def _fallback_practices(crop_key: str) -> list[str]:
    """Used only if KB load fails — minimal safe defaults."""
    if crop_key == "tomato":
        return [
            "Store at 12–15°C with 85–90% RH.",
            "Inspect daily for softening or mould.",
            "Remove damaged fruits immediately.",
        ]
    return [
        "Maintain grain moisture ≤14%.",
        "Protect from insects, rodents, and birds.",
        "Inspect storage regularly.",
    ]


def _build_recommendations(
    crop_key: str,
    storage_type: str,
    spoilage_risk: str,
    storage_health: str,
    risk_factors: list[str],
    shelf_pct: float,
    latest_log: Optional[dict],
) -> list[dict]:
    """
    Build an ordered list of concrete actions based on the assessment.
    Priority 1 = most urgent. Rules are additive — all that apply are included.
    """
    recs = []
    priority = 1

    def add(action: str, reason: str, urgency: str):
        nonlocal priority
        recs.append({
            "priority": priority,
            "action": action,
            "reason": reason,
            "urgency": urgency,
        })
        priority += 1

    # Critical visual condition — always first
    if latest_log and latest_log.get("visual_condition") == "critical":
        add(
            action="Segregate and dispose of spoiled stock immediately.",
            reason="Critical spoilage detected visually — affected produce cannot be saved and will accelerate losses in healthy stock.",
            urgency="immediate",
        )

    # Past shelf life
    if shelf_pct >= 100:
        add(
            action="Move produce to market or process immediately.",
            reason="Estimated shelf life has been exceeded. Further storage risks complete loss.",
            urgency="immediate",
        )

    # Early spoilage visual
    if latest_log and latest_log.get("visual_condition") == "early_spoilage":
        add(
            action="Sort stock — remove all affected units before spoilage spreads.",
            reason="Early spoilage detected. Isolating affected produce now prevents spread to healthy stock.",
            urgency="within_24h",
        )

    # High temperature
    temp = latest_log.get("temperature_c") if latest_log else None
    optimal = OPTIMAL_CONDITIONS.get(crop_key, {})
    if temp is not None and optimal.get("temp_max_c") and temp > optimal["temp_max_c"]:
        if crop_key == "tomato":
            add(
                action="Lower storage temperature to 12–15°C.",
                reason=f"Current temperature {temp}°C accelerates ripening and microbial growth. Target range per knowledge base: 12–15°C.",
                urgency="within_24h",
            )
        else:
            add(
                action="Improve ventilation or move grain to a cooler storage area.",
                reason=f"Temperature {temp}°C is above safe range — elevated temperature promotes mould and insect activity in stored grain.",
                urgency="within_24h",
            )

    # High humidity (rice)
    humidity = latest_log.get("humidity_percent") if latest_log else None
    if humidity is not None and crop_key == "rice" and optimal.get("humidity_max") and humidity > optimal["humidity_max"]:
        add(
            action="Re-dry grain or seal storage to prevent moisture ingress.",
            reason=f"Humidity {humidity}% exceeds safe maximum of {optimal['humidity_max']}%. Moisture above this level risks mould and quality loss.",
            urgency="within_24h",
        )

    # Low humidity (tomato)
    if humidity is not None and crop_key == "tomato" and optimal.get("humidity_min") and humidity < optimal["humidity_min"]:
        add(
            action="Increase storage humidity to 85–90% RH.",
            reason=f"Current humidity {humidity}% is below the 85–90% RH range — tomatoes will dehydrate and lose marketable quality.",
            urgency="within_24h",
        )

    # Open storage
    if storage_type == "open":
        add(
            action="Move produce to covered or enclosed storage as soon as possible.",
            reason="Open storage exposes produce to weather, pests, and birds — quality loss will be rapid.",
            urgency="within_24h",
        )

    # Shelf life 80–100% — plan to sell
    if 80 <= shelf_pct < 100 and spoilage_risk in ("moderate", "high"):
        add(
            action="Plan immediate sale or processing — do not wait for the next market cycle.",
            reason=f"Shelf life is {shelf_pct:.0f}% consumed. Waiting risks complete loss rather than partial.",
            urgency="within_week",
        )

    # Routine inspection — always added if no critical issues dominate
    if spoilage_risk in ("low", "moderate") and shelf_pct < 80:
        add(
            action="Continue routine condition checks per recommended schedule.",
            reason="Current conditions are within acceptable range. Regular monitoring is the primary safeguard against undetected deterioration.",
            urgency="routine",
        )

    return recs


# ---------------------------------------------------------------------------
# Summary strings
# ---------------------------------------------------------------------------

def _health_summary(storage_health: str, days: int, crop_key: str) -> str:
    summaries = {
        "optimal":    f"Storage conditions are optimal for {crop_key}. Produce in good standing at day {days}.",
        "acceptable": f"Storage conditions are acceptable. Minor issues detected — monitor and correct where possible.",
        "at_risk":    f"Storage conditions are at risk. One or more factors are outside safe ranges — action needed soon.",
        "critical":   f"Storage conditions are critical. Immediate intervention required to prevent total loss.",
    }
    return summaries.get(storage_health, "Assessment unavailable.")


def _spoilage_summary(spoilage_risk: str, shelf: dict, crop_key: str) -> str:
    remaining = shelf["remaining_shelf_life_days"]
    consumed = shelf["shelf_life_consumed_percent"]
    summaries = {
        "low":      f"Low spoilage risk. Approximately {remaining} days of shelf life remaining ({consumed:.0f}% consumed).",
        "moderate": f"Moderate spoilage risk. Approximately {remaining} days remaining — conditions require attention.",
        "high":     f"High spoilage risk. Only {remaining} days of estimated shelf life remaining. Act promptly.",
        "critical": f"Critical spoilage risk. Shelf life exceeded or severe condition failure. Immediate action required.",
    }
    return summaries.get(spoilage_risk, "Spoilage risk unknown.")