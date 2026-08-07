"""
app/engines/decision_optimization/topsis.py

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

Takes the candidate actions from alternative_builder.py and the criteria
weights from ahp.py, and produces a ranked list: each action gets a
closeness score in [0, 1] (higher = closer to the ideal action, farther
from the worst-case action), sorted descending.

Standard TOPSIS steps, implemented with plain Python (no numpy dependency,
consistent with ahp.py):
    1. Build the decision matrix (rows = alternatives, cols = criteria)
    2. Vector-normalize each column
    3. Apply AHP weights
    4. Determine the ideal-best and ideal-worst value per column
       (benefit criteria: best = max, worst = min — and reversed for cost)
    5. Compute each alternative's Euclidean distance to both
    6. Closeness coefficient = distance-to-worst / (distance-to-best + distance-to-worst)
"""

import math
from typing import Optional

from .ahp import CRITERIA, CRITERIA_DIRECTIONS, get_criteria_weights


def build_decision_matrix(alternatives: list[dict], criteria: list[str]) -> list[list[float]]:
    """
    Missing criteria on an alternative default to 0.0 rather than raising —
    consistent with the rest of this engine's "degrade gracefully" approach
    (a malformed alternative shouldn't crash the whole ranking).
    """
    return [
        [float(alt.get(c, 0.0)) for c in criteria]
        for alt in alternatives
    ]


def normalize_matrix(matrix: list[list[float]]) -> list[list[float]]:
    """
    Vector normalization per column: x_ij / sqrt(sum(x_ij^2)).
    If a column is all zeros (e.g. every candidate has loss=0), it can't
    discriminate between alternatives anyway — left as all zeros rather
    than dividing by zero.
    """
    if not matrix:
        return []
    n_rows, n_cols = len(matrix), len(matrix[0])
    col_norms = []
    for j in range(n_cols):
        sq_sum = sum(matrix[i][j] ** 2 for i in range(n_rows))
        col_norms.append(math.sqrt(sq_sum))

    normalized = []
    for i in range(n_rows):
        row = []
        for j in range(n_cols):
            norm = col_norms[j]
            row.append(matrix[i][j] / norm if norm > 0 else 0.0)
        normalized.append(row)
    return normalized


def apply_weights(normalized_matrix: list[list[float]], weights: list[float]) -> list[list[float]]:
    return [
        [value * weights[j] for j, value in enumerate(row)]
        for row in normalized_matrix
    ]


def determine_ideal_solutions(
    weighted_matrix: list[list[float]], directions: list[str]
) -> tuple[list[float], list[float]]:
    """
    Per column: for a benefit criterion, ideal-best is the max and
    ideal-worst is the min. For a cost criterion, it's reversed.
    """
    if not weighted_matrix:
        return [], []
    n_cols = len(weighted_matrix[0])
    ideal_best = []
    ideal_worst = []
    for j in range(n_cols):
        column = [row[j] for row in weighted_matrix]
        if directions[j] == "cost":
            ideal_best.append(min(column))
            ideal_worst.append(max(column))
        else:  # "benefit"
            ideal_best.append(max(column))
            ideal_worst.append(min(column))
    return ideal_best, ideal_worst


def compute_distances(
    weighted_matrix: list[list[float]],
    ideal_best: list[float],
    ideal_worst: list[float],
) -> tuple[list[float], list[float]]:
    dist_best = []
    dist_worst = []
    for row in weighted_matrix:
        dist_best.append(math.sqrt(sum((row[j] - ideal_best[j]) ** 2 for j in range(len(row)))))
        dist_worst.append(math.sqrt(sum((row[j] - ideal_worst[j]) ** 2 for j in range(len(row)))))
    return dist_best, dist_worst


def compute_closeness(dist_best: list[float], dist_worst: list[float]) -> list[float]:
    """
    C_i = dist_worst_i / (dist_best_i + dist_worst_i). Higher is better.
    If an alternative sits exactly at both the ideal best AND worst
    simultaneously (only possible when every alternative is identical on
    every criterion), both distances are 0 — scored 0.5 (neutral) rather
    than dividing by zero.
    """
    closeness = []
    for db, dw in zip(dist_best, dist_worst):
        total = db + dw
        closeness.append(dw / total if total > 0 else 0.5)
    return closeness


def rank_alternatives(
    alternatives: list[dict],
    criteria: Optional[list[str]] = None,
    weights: Optional[dict] = None,
    directions: Optional[dict] = None,
) -> list[dict]:
    """
    Full TOPSIS pipeline. Returns the input alternatives, each with a
    "score" (closeness coefficient, 0-1) and "rank" (1 = best) added,
    sorted descending by score. Original fields (task, urgency, risk,
    loss, effort, source, ...) are preserved untouched.

    weights: dict like {"urgency": 0.17, "risk": 0.29, ...} — defaults to
        ahp.get_criteria_weights() if not supplied.
    directions: dict like {"urgency": "benefit", "effort": "cost"} —
        defaults to ahp.CRITERIA_DIRECTIONS if not supplied.
    """
    if not alternatives:
        return []

    criteria = criteria or CRITERIA
    directions = directions or CRITERIA_DIRECTIONS
    direction_list = [directions[c] for c in criteria]

    if weights is None:
        weights = get_criteria_weights(criteria)["weights"]
    weight_list = [weights[c] for c in criteria]

    matrix = build_decision_matrix(alternatives, criteria)
    normalized = normalize_matrix(matrix)
    weighted = apply_weights(normalized, weight_list)
    ideal_best, ideal_worst = determine_ideal_solutions(weighted, direction_list)
    dist_best, dist_worst = compute_distances(weighted, ideal_best, ideal_worst)
    scores = compute_closeness(dist_best, dist_worst)

    ranked = [
        {**alt, "score": round(score, 4)}
        for alt, score in zip(alternatives, scores)
    ]
    ranked.sort(key=lambda a: a["score"], reverse=True)
    for i, alt in enumerate(ranked, start=1):
        alt["rank"] = i

    return ranked


if __name__ == "__main__":
    import json

    sample_alternatives = [
        {
            "task": "Treat TYLCV \u2014 confirmed by detection and expected at this stage",
            "urgency": 0.7, "risk": 0.6, "loss": 21830.0, "effort": 0.4,
            "source": "disease_confirmed",
        },
        {
            "task": "Scout for sheath_blight \u2014 expected this stage, not yet confirmed",
            "urgency": 0.3, "risk": 0.6, "loss": 0.0, "effort": 0.2,
            "source": "disease_expected_unconfirmed",
        },
        {
            "task": "Inspect crop for fungal disease \u2014 humidity is elevated",
            "urgency": 0.5, "risk": 0.5, "loss": 0.0, "effort": 0.3,
            "source": "weather",
        },
        {
            "task": "Schedule irrigation \u2014 prolonged dry spell detected",
            "urgency": 0.8, "risk": 0.7, "loss": 0.0, "effort": 0.6,
            "source": "weather",
        },
        {
            "task": "Control weeds.",
            "urgency": 0.4, "risk": 0.4, "loss": 0.0, "effort": 0.5,
            "source": "workflow_pending",
        },
    ]

    result = rank_alternatives(sample_alternatives)
    print(json.dumps(result, indent=2))