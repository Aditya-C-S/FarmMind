"""
app/engines/decision_optimization/__init__.py

Public entry point for the Decision Optimization engine, matching the
convention already used by app/engines/workflow (get_daily_workflow) and
app/engines/context_fusion (get_fused_context).
"""

from .alternative_builder import build_alternatives
from .ahp import get_criteria_weights, CRITERIA, CRITERIA_DIRECTIONS
from .topsis import rank_alternatives


def get_ranked_actions(fused_context: dict, workflow: dict = None, judgments: dict = None) -> list[dict]:
    """
    Full pipeline: fused context -> candidate actions -> AHP weights -> TOPSIS ranking.

    fused_context: output of get_fused_context() (Phase 4)
    workflow: optional raw get_daily_workflow() response, passed through to
        build_alternatives() as a fallback source of pending task text
    judgments: optional AHP pairwise judgments override, passed through to
        get_criteria_weights(). Uses the project defaults if omitted.

    Returns a list of ranked action dicts:
        {"task", "urgency", "risk", "loss", "effort", "source", "score", "rank"}
    sorted best-first (rank 1 = top priority).
    """
    alternatives = build_alternatives(fused_context, workflow=workflow)
    if not alternatives:
        return []

    weights = get_criteria_weights(judgments=judgments)["weights"]
    return rank_alternatives(alternatives, weights=weights)