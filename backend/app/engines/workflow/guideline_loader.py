"""
Guideline Loader
----------------
Given a stage_id (already known from StageResolver — no re-searching
growth_timeline here) and the crop knowledge base, fetches the matching
detailed entry from stage_guidelines.

Also expands common_pests / common_diseases from bare {pest_id, risk_level}
references into the full pest/disease objects (identification, management,
etc.), since the dashboard needs the actual guidance text, not just an ID.
"""

from typing import Any, Dict, List

from app.knowledge.treatment_lookup import get_preventive_treatment


class GuidelineNotFoundError(Exception):
    """Raised when a stage_id has no matching entry in stage_guidelines."""


def _index_by_id(items: List[Dict[str, Any]], id_field: str) -> Dict[str, Dict[str, Any]]:
    """Build a {id: item} lookup, skipping any item missing the id field."""
    return {item[id_field]: item for item in items if id_field in item}


def load_guidelines(
    crop_data: Dict[str, Any],
    stage_id: str,
    expand_references: bool = True,
) -> Dict[str, Any]:
    """
    Fetch the stage_guidelines entry for a given stage_id.

    Args:
        crop_data: full crop knowledge base
        stage_id: e.g. "tillering" — taken directly from
                  stage_resolver's current_stage["stage_id"], not re-derived
        expand_references: if True (default), common_pests/common_diseases
                  entries are enriched with the full pest/disease object
                  (identification, management, etc.) alongside their
                  stage-specific risk_level/monitor flags. If False,
                  returns the raw {pest_id, risk_level, monitor} shape.

    Returns:
        The stage_guidelines object for stage_id (shallow copy — the
        cached crop_data is never mutated).

    Raises:
        GuidelineNotFoundError: if stage_id has no entry in stage_guidelines.
            This would indicate a data bug (growth_timeline and
            stage_guidelines have gotten out of sync) rather than bad
            user input, since stage_id normally comes from StageResolver.
    """
    stage_guidelines = crop_data.get("stage_guidelines", [])
    guidelines_by_id = _index_by_id(stage_guidelines, "stage_id")

    if stage_id not in guidelines_by_id:
        raise GuidelineNotFoundError(
            f"No stage_guidelines entry found for stage_id '{stage_id}'. "
            f"growth_timeline and stage_guidelines may be out of sync in "
            f"'{crop_data.get('crop_id', 'this crop')}'s knowledge base."
        )

    guideline = dict(guidelines_by_id[stage_id])  # shallow copy, don't mutate cache

    if expand_references:
        pests_by_id = _index_by_id(crop_data.get("pests", []), "pest_id")
        diseases_by_id = _index_by_id(crop_data.get("diseases", []), "disease_id")

        guideline["common_pests"] = [
            {**pests_by_id[ref["pest_id"]], "risk_level": ref.get("risk_level"), "monitor": ref.get("monitor")}
            for ref in guideline.get("common_pests", [])
            if ref.get("pest_id") in pests_by_id
        ]
        guideline["common_diseases"] = [
            {**diseases_by_id[ref["disease_id"]], "risk_level": ref.get("risk_level"), "monitor": ref.get("monitor"), "treatment": get_preventive_treatment(ref["disease_id"])}
            for ref in guideline.get("common_diseases", [])
            if ref.get("disease_id") in diseases_by_id
        ]

    return guideline