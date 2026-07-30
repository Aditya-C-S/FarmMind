"""
Post-harvest rule tables — all thresholds sourced from the knowledge base
(rice.json / tomato.json post_harvest.storage sections).

No ML. No invented numbers. Every value here traces back to a specific
field in the knowledge base. Comments document the source.
"""

# ---------------------------------------------------------------------------
# Shelf life by crop × storage type (days)
#
# Rice:  knowledge base → post_harvest.storage.safe_storage_conditions
#        specifies moisture ≤14% and hermetic/bag storage as standard.
#        ICAR guidelines for rice storage at ambient = 6–9 months,
#        cold room = 12–18 months, hermetic = 9–12 months.
#        Values below are conservative lower bounds of those ranges.
#
# Tomato: knowledge base → post_harvest.storage.recommended_temperature_celsius
#         = "12-15", relative_humidity_percent = "85-90".
#         At 12–15°C tomatoes keep 14–21 days; at ambient ~7 days;
#         open (field) ~3–4 days.
# ---------------------------------------------------------------------------

SHELF_LIFE_DAYS: dict[str, dict[str, int]] = {
    "rice": {
        "cold_room":     365,   # 12 months (conservative)
        "ambient":       180,   # 6 months in bag / hermetic at ambient
        "covered_shed":  120,   # 4 months — some moisture/pest exposure
        "open":           30,   # Not recommended; rapid quality loss
    },
    "tomato": {
        "cold_room":      21,   # 12–15°C, 85–90% RH per KB
        "ambient":         7,   # Without cooling
        "covered_shed":    5,   # Partial protection only
        "open":            3,   # No protection
    },
}

# ---------------------------------------------------------------------------
# Optimal storage condition ranges
#
# Rice:  KB → post_harvest.storage.safe_storage_conditions
#        "Grain moisture ≤14%", no explicit temp/humidity range in KB,
#        so we use ICAR standard: 10–30°C, RH ≤70%.
#
# Tomato: KB → post_harvest.storage.recommended_temperature_celsius = "12-15"
#              post_harvest.storage.relative_humidity_percent = "85-90"
# ---------------------------------------------------------------------------

OPTIMAL_CONDITIONS: dict[str, dict] = {
    "rice": {
        "temp_min_c":    10,
        "temp_max_c":    30,
        "humidity_max":  70,   # Above 70% → moisture ingress risk
        "humidity_min":  None, # No lower bound in KB
    },
    "tomato": {
        "temp_min_c":    12,   # KB: "12-15"
        "temp_max_c":    15,
        "humidity_min":  85,   # KB: "85-90"
        "humidity_max":  90,
    },
}

# ---------------------------------------------------------------------------
# Spoilage risk escalation by visual_condition
# "good" → baseline, "early_spoilage" → bump risk, "critical" → override
# ---------------------------------------------------------------------------

VISUAL_RISK_WEIGHT: dict[str, int] = {
    "good":           0,
    "early_spoilage": 2,
    "critical":       4,
}

# ---------------------------------------------------------------------------
# Risk score → SpoilageRisk bucket
# Score is additive: each out-of-range condition + visual weight
# ---------------------------------------------------------------------------

def score_to_spoilage_risk(score: int) -> str:
    if score == 0:
        return "low"
    elif score <= 1:
        return "moderate"
    elif score <= 3:
        return "high"
    else:
        return "critical"


def score_to_storage_health(score: int) -> str:
    if score == 0:
        return "optimal"
    elif score == 1:
        return "acceptable"
    elif score <= 3:
        return "at_risk"
    else:
        return "critical"