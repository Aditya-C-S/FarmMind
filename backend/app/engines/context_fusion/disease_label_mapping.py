"""
Disease Label Mapping
---------------------
Aditya's disease detection pipeline (run_pipeline()) outputs a human/model
label like "TYLCV" or "Sheath Blight". The crop knowledge base JSON uses
its own disease_id slugs ("tomato_leaf_curl_virus", "sheath_blight"). These
don't match as strings, so a naive equality check would silently fail
every single time. This module is the one place that translation happens.

MVP scope (per team decision): only two diseases are covered —
TYLCV (tomato) and Sheath Blight (rice). Extend this table as Aditya's
model adds more disease classes; nothing else in Context Fusion needs to
change when that happens.
"""

from typing import Optional

# Confirmed mapping for MVP scope. Keys are normalized (uppercased, stripped)
# so minor casing differences from the model don't cause a silent miss.
_LABEL_TO_DISEASE_ID = {
    "TYLCV": "tomato_leaf_curl_virus",
    "TOMATO LEAF CURL VIRUS": "tomato_leaf_curl_virus",
    "SHEATH BLIGHT": "sheath_blight",
}


def normalize_label(label: str) -> str:
    """Normalize a model output label for lookup (uppercase, strip whitespace)."""
    return label.strip().upper()


def label_to_disease_id(label: str) -> Optional[str]:
    """
    Translate a disease detection model label into the disease_id used in
    the crop knowledge base.

    Args:
        label: raw label from run_pipeline(), e.g. "TYLCV"

    Returns:
        The matching disease_id (e.g. "tomato_leaf_curl_virus"), or None if
        the label isn't in the MVP mapping table. Callers should treat None
        as "detected something outside current MVP scope" rather than crash —
        Aditya's model may eventually support more diseases than the
        knowledge base has entries for yet, or vice versa.
    """
    return _LABEL_TO_DISEASE_ID.get(normalize_label(label))