from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.ai.types import DetectionResult


@lru_cache
def _load_synonyms() -> dict[str, str]:
    """Load synonym mappings from config/synonyms.json.

    Keys and values are treated case-insensitively; keys are normalized to lowercase.
    """
    project_root = Path(__file__).resolve().parents[2]
    synonyms_path = project_root / "config" / "synonyms.json"

    if not synonyms_path.exists():
        return {}

    with synonyms_path.open("r", encoding="utf-8") as f:
        raw: dict[str, str] = json.load(f)

    return {k.lower().strip(): v.lower().strip() for k, v in raw.items()}


def normalize_label(label: str) -> str:
    """Normalize a single label using synonyms config."""
    if not label:
        return label

    synonyms = _load_synonyms()
    key = label.lower().strip()
    return synonyms.get(key, key)


def normalize_detection(det: DetectionResult) -> DetectionResult:
    """Return a copy of `DetectionResult` with normalized label."""
    normalized_label = normalize_label(det.label)
    return DetectionResult(label=normalized_label, confidence=det.confidence)


def normalize_detections(detections: list[DetectionResult]) -> list[DetectionResult]:
    """Normalize labels for a list of detections."""
    return [normalize_detection(d) for d in detections]

