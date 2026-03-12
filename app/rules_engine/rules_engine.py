from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

from app.ai.detection_service import DetectionResult
from app.ai.normalization import normalize_label


@dataclass
class AssetClassification:
    label: str
    normalized_label: str
    asset_life_years: int
    category: str
    description: str | None = None
    confidence: float | None = None


@lru_cache
def _load_asset_rules() -> dict[str, dict]:
    """Load asset classification rules from rules/asset_rules.json."""
    project_root = Path(__file__).resolve().parents[2]
    rules_path = project_root / "rules" / "asset_rules.json"

    if not rules_path.exists():
        return {}

    with rules_path.open("r", encoding="utf-8") as f:
        data: dict[str, dict] = json.load(f)

    # Normalize keys to lowercase for case-insensitive lookup
    return {k.lower().strip(): v for k, v in data.items()}


def classify_label(label: str, confidence: Optional[float] = None) -> Optional[AssetClassification]:
    """Classify a single asset label into cost segregation terms.

    Returns None if no rule is found for the normalized label.
    """
    if not label:
        return None

    normalized = normalize_label(label)
    rules = _load_asset_rules()
    rule = rules.get(normalized)

    if not rule:
        return None

    return AssetClassification(
        label=label,
        normalized_label=normalized,
        asset_life_years=int(rule.get("asset_life_years", 39)),
        category=str(rule.get("category", "structural")),
        description=rule.get("description"),
        confidence=confidence,
    )


def classify_detections(detections: Iterable[DetectionResult]) -> List[AssetClassification]:
    """Classify a sequence of DetectionResult objects into asset classifications."""
    results: list[AssetClassification] = []

    for det in detections:
        classification = classify_label(det.label, confidence=det.confidence)
        if classification:
            results.append(classification)

    return results

