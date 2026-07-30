"""
Disease Context
---------------
Merges two different kinds of disease signal:

1. EXPECTED risk — from the Workflow Engine's guidance.disease_alerts,
   already resolved for the current growth stage (knowledge-base driven,
   no camera involved).
2. DETECTED reality — from Aditya's run_pipeline() output (visual model
   inference on an actual photo).

The point of "fusion" here: a disease that's both expected AND detected is
a much stronger signal than either alone. A disease detected that ISN'T
expected at this stage is worth flagging as unusual rather than trusting
silently. And an expected disease with no detection yet is still worth
showing — it just means nobody's checked yet, not that it's not a risk.

Severity-class -> risk-level mapping below is a best-effort heuristic
since the exact vocabulary Aditya's severity_class field uses long-term
isn't fully confirmed yet (we've only seen "Moderate" in one example
output). Extend _SEVERITY_TO_RISK_LEVEL as more values are observed.
"""

from typing import Any, Dict, List, Optional

from app.engines.context_fusion.disease_label_mapping import label_to_disease_id

_RISK_LEVEL_ORDER = {"Low": 0, "Medium": 1, "High": 2}

_SEVERITY_TO_RISK_LEVEL = {
    "MILD": "Low",
    "LOW": "Low",
    "MODERATE": "Medium",
    "MEDIUM": "Medium",
    "SEVERE": "High",
    "HIGH": "High",
    "CRITICAL": "High",
}


def _severity_to_risk_level(severity_class: Optional[str]) -> Optional[str]:
    if not severity_class:
        return None
    return _SEVERITY_TO_RISK_LEVEL.get(severity_class.strip().upper())


def _combine_risk_level(expected: Optional[str], from_severity: Optional[str]) -> Optional[str]:
    """Take the higher of the two risk levels, when both are known."""
    candidates = [r for r in (expected, from_severity) if r in _RISK_LEVEL_ORDER]
    if not candidates:
        return expected or from_severity
    return max(candidates, key=lambda r: _RISK_LEVEL_ORDER[r])


def get_disease_context(
    workflow_disease_alerts: List[Dict[str, Any]],
    detections: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Merge expected (knowledge-base) disease risk with detected (visual
    model) disease findings for the current stage.

    Args:
        workflow_disease_alerts: guidance.disease_alerts from the Workflow
            Engine's response — full disease objects already expanded,
            each with a disease_id and stage-specific risk_level.
        detections: list of run_pipeline()-shaped dicts, e.g.
            {"crop": "Rice", "disease": "Sheath Blight", "confidence": 91.3,
             "severity_score": 32.4, "severity_class": "Moderate",
             "occurrence_prob": 71.6, "progression": "Worsening",
             "economic_loss": {...}}
            Pass an empty list if no photo has been analyzed yet.

    Returns:
        {
            "confirmed": [...],           # expected AND detected — strongest signal
            "unexpected_detections": [...], # detected but NOT expected at this stage
            "expected_unconfirmed": [...],  # expected, but no matching detection yet
            "unmapped_detections": [...],   # detected a label outside current MVP scope
        }
    """
    expected_by_id = {d["disease_id"]: d for d in workflow_disease_alerts}
    confirmed_ids = set()

    confirmed: List[Dict[str, Any]] = []
    unexpected: List[Dict[str, Any]] = []
    unmapped: List[Dict[str, Any]] = []

    for detection in detections:
        raw_label = detection.get("disease")
        disease_id = label_to_disease_id(raw_label) if raw_label else None

        if disease_id is None:
            unmapped.append({"raw_label": raw_label, "detection": detection})
            continue

        severity_risk = _severity_to_risk_level(detection.get("severity_class"))

        if disease_id in expected_by_id:
            expected = expected_by_id[disease_id]
            confirmed_ids.add(disease_id)
            confirmed.append(
                {
                    "disease_id": disease_id,
                    "common_name": expected.get("common_name"),
                    "expected_risk_level": expected.get("risk_level"),
                    "detected_severity_class": detection.get("severity_class"),
                    "combined_risk_level": _combine_risk_level(
                        expected.get("risk_level"), severity_risk
                    ),
                    "confidence": detection.get("confidence"),
                    "progression": detection.get("progression"),
                    "economic_loss": detection.get("economic_loss"),
                }
            )
        else:
            unexpected.append(
                {
                    "disease_id": disease_id,
                    "confidence": detection.get("confidence"),
                    "severity_class": detection.get("severity_class"),
                    "progression": detection.get("progression"),
                    "economic_loss": detection.get("economic_loss"),
                    "note": "Detected, but not a typical risk at the current growth stage — worth double-checking.",
                }
            )

    expected_unconfirmed = [
        {
            "disease_id": disease_id,
            "common_name": expected.get("common_name"),
            "risk_level": expected.get("risk_level"),
        }
        for disease_id, expected in expected_by_id.items()
        if disease_id not in confirmed_ids
    ]

    return {
        "confirmed": confirmed,
        "unexpected_detections": unexpected,
        "expected_unconfirmed": expected_unconfirmed,
        "unmapped_detections": unmapped,
    }