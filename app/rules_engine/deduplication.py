from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Tuple


def deduplicate_assets(labels: Iterable[str]) -> List[Tuple[str, int]]:
    """Collapse multiple detections of the same object into a single asset count of 1.

    Example:
        ["mirror", "mirror", "mirror", "sink", "sink"] -> [("mirror", 1), ("sink", 1)]
    """
    unique = {label.strip().lower() for label in labels if label and label.strip()}
    return [(label, 1) for label in sorted(unique)]


def count_assets(labels: Iterable[str]) -> List[Tuple[str, int]]:
    """Return frequency counts per label (if you need full detection counts).

    Example:
        ["mirror", "mirror", "mirror", "sink", "sink"] -> [("mirror", 3), ("sink", 2)]
    """
    cleaned = [label.strip().lower() for label in labels if label and label.strip()]
    counts = Counter(cleaned)
    return sorted(counts.items())

