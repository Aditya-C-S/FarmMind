"""
Crop Loader
-----------
Loads crop knowledge base JSON files from app/knowledge/.

Schema-agnostic on purpose: this module does not know what a "stage" or
a "pest" is. It only knows how to find a file named {crop_id}.json and
parse it. Any crop that follows the unified schema works automatically —
no code changes needed to add wheat.json, potato.json, etc.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

# app/engines/workflow/crop_loader.py -> app/knowledge/
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge"


class CropNotFoundError(Exception):
    """Raised when no knowledge base file exists for the requested crop."""


class CropLoadError(Exception):
    """Raised when a knowledge base file exists but contains invalid JSON."""


@lru_cache(maxsize=32)
def load_crop(crop_id: str) -> Dict[str, Any]:
    """
    Load the knowledge base for a given crop.

    Cached in memory (lru_cache) since knowledge base files are read
    frequently (every workflow request) but change rarely. Call
    clear_cache() after editing a JSON file on disk if the process is
    still running.

    Args:
        crop_id: e.g. "rice", "tomato" — matched case-insensitively
                 against the filename in app/knowledge/.

    Returns:
        Parsed JSON knowledge base as a dict.

    Raises:
        CropNotFoundError: if no {crop_id}.json exists in app/knowledge/
        CropLoadError: if the file exists but isn't valid JSON
    """
    path = KNOWLEDGE_DIR / f"{crop_id.lower()}.json"

    if not path.exists():
        available = list_supported_crops()
        raise CropNotFoundError(
            f"No knowledge base found for crop '{crop_id}' (expected {path}). "
            f"Currently supported crops: {available or '[]'}"
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise CropLoadError(
            f"Knowledge base file '{path.name}' contains invalid JSON: {e}"
        ) from e


def list_supported_crops() -> List[str]:
    """Dynamically discover every crop with a knowledge base file on disk."""
    if not KNOWLEDGE_DIR.exists():
        return []
    return sorted(p.stem for p in KNOWLEDGE_DIR.glob("*.json"))


def clear_cache() -> None:
    """Clear the in-memory crop cache. Use after editing a knowledge base file."""
    load_crop.cache_clear()