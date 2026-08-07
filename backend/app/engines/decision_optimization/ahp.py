"""
app/engines/decision_optimization/ahp.py

AHP (Analytic Hierarchy Process) — criteria weighting.

Takes pairwise importance judgments between criteria (Saaty 1-9 scale) and
produces a normalized weight vector, using the row geometric mean method
(numerically simpler and just as reliable as the full eigenvector method
for a small criteria set like this one). Also reports a consistency ratio
(CR) so a contradictory set of judgments doesn't silently poison the
weights that TOPSIS will rank against.

This module only produces WEIGHTS. Whether a criterion should be
maximized or minimized during ranking (benefit vs cost) is a TOPSIS-side
concern — CRITERIA_DIRECTIONS below is defined here because it belongs
conceptually with the criteria list, but AHP itself doesn't use it.
"""

import math
from typing import Optional


CRITERIA = ["urgency", "risk", "loss", "effort"]

# TOPSIS will need this — urgency/risk/loss are "more is more important to
# act on", effort is "more is worse" (harder/costlier to do).
CRITERIA_DIRECTIONS = {
    "urgency": "benefit",
    "risk": "benefit",
    "loss": "benefit",
    "effort": "cost",
}

# Saaty's Random Index, for consistency ratio calculation. Indexed by n
# (number of criteria).
RANDOM_INDEX = {
    1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
}

# Default pairwise judgments: loss > risk > urgency > effort.
# Read as (a, b): value meaning "a is `value` times as important as b" on
# the Saaty 1-9 scale. Reciprocals are filled in automatically — you only
# specify each pair once. Tune this to your own domain expert's judgment;
# this is a starting point, not a fixed truth.
DEFAULT_JUDGMENTS = {
    ("loss", "risk"): 2,
    ("loss", "urgency"): 3,
    ("loss", "effort"): 5,
    ("risk", "urgency"): 2,
    ("risk", "effort"): 4,
    ("urgency", "effort"): 3,
}


def build_pairwise_matrix(criteria: list[str], judgments: dict) -> list[list[float]]:
    """
    Builds an n x n pairwise comparison matrix from a sparse judgments dict.
    Unspecified pairs default to 1 (equal importance) — diagonal is always 1.
    """
    n = len(criteria)
    index = {c: i for i, c in enumerate(criteria)}
    matrix = [[1.0] * n for _ in range(n)]

    for (a, b), value in judgments.items():
        if a not in index or b not in index:
            raise ValueError(f"Judgment references unknown criterion: {a!r} or {b!r}")
        i, j = index[a], index[b]
        value = float(value)
        matrix[i][j] = value
        matrix[j][i] = 1.0 / value

    return matrix


def compute_weights(matrix: list[list[float]]) -> dict:
    """
    Row geometric mean method + consistency check.

    Returns:
        {
            "weights": [w1, ..., wn],       # sums to 1.0
            "lambda_max": float,
            "consistency_index": float,
            "consistency_ratio": float,
            "consistent": bool,             # CR <= 0.1 is the standard threshold
        }
    """
    n = len(matrix)

    row_geo_means = []
    for row in matrix:
        product = 1.0
        for value in row:
            product *= value
        row_geo_means.append(product ** (1.0 / n))

    total = sum(row_geo_means)
    weights = [gm / total for gm in row_geo_means]

    # Consistency check: how close is this matrix to being perfectly
    # transitive, given the weights we just derived from it?
    weighted_sums = [
        sum(matrix[i][j] * weights[j] for j in range(n))
        for i in range(n)
    ]
    lambda_values = [weighted_sums[i] / weights[i] for i in range(n)]
    lambda_max = sum(lambda_values) / n

    consistency_index = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    random_index = RANDOM_INDEX.get(n, 1.49)  # fall back to the n=10 value for larger sets
    consistency_ratio = (consistency_index / random_index) if random_index > 0 else 0.0

    return {
        "weights": weights,
        "lambda_max": lambda_max,
        "consistency_index": consistency_index,
        "consistency_ratio": consistency_ratio,
        "consistent": consistency_ratio <= 0.1,
    }


def get_criteria_weights(
    criteria: Optional[list[str]] = None,
    judgments: Optional[dict] = None,
) -> dict:
    """
    Convenience wrapper: criteria names -> weight, plus consistency metadata.

    Does NOT raise if the judgments are inconsistent (CR > 0.1) — mirrors
    this project's existing philosophy (weather returns data_available:
    False rather than crashing, fertilizer gaps show "Pending Validation").
    It flags the problem via "consistent": False and lets the caller decide
    whether to use the weights anyway, fall back to equal weights, or
    surface a warning to whoever owns the pairwise judgments.

    Example:
        >>> result = get_criteria_weights()
        >>> result["weights"]
        {'urgency': 0.17, 'risk': 0.29, 'loss': 0.47, 'effort': 0.07}
        >>> result["consistent"]
        True
    """
    criteria = criteria or CRITERIA
    judgments = judgments if judgments is not None else DEFAULT_JUDGMENTS

    matrix = build_pairwise_matrix(criteria, judgments)
    result = compute_weights(matrix)

    return {
        "weights": {c: round(w, 4) for c, w in zip(criteria, result["weights"])},
        "lambda_max": round(result["lambda_max"], 4),
        "consistency_ratio": round(result["consistency_ratio"], 4),
        "consistent": result["consistent"],
    }


if __name__ == "__main__":
    import json

    result = get_criteria_weights()
    print(json.dumps(result, indent=2))

    if not result["consistent"]:
        print(
            f"\nWarning: CR = {result['consistency_ratio']} exceeds 0.1 — "
            "these pairwise judgments aren't internally consistent enough "
            "to trust the derived weights. Revisit DEFAULT_JUDGMENTS."
        )