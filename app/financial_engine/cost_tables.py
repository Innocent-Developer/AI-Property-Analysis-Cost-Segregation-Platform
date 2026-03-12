"""Load unit replacement costs from config/cost_tables.json (config-driven)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional


@lru_cache
def _load_cost_tables() -> dict[str, float]:
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "config" / "cost_tables.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {str(k).lower().strip(): float(v) for k, v in raw.items()}


def get_unit_cost(asset_name: str) -> Optional[float]:
    """Return configured unit replacement cost for asset name, or None if not in cost_tables."""
    tables = _load_cost_tables()
    key = asset_name.lower().strip()
    return tables.get(key)
