"""Shared types for the AI module (avoids circular imports)."""
from dataclasses import dataclass


@dataclass
class DetectionResult:
    label: str
    confidence: float
