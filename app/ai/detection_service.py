from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

from app.ai.normalization import normalize_detections
from app.pipelines.image_preprocessing import preprocess_images_for_detection


@dataclass
class DetectionResult:
    label: str
    confidence: float


class BaseOpenVocabularyDetector:
    """Model 1: open-vocabulary object detector."""

    async def detect(self, image: np.ndarray) -> List[DetectionResult]:  # pragma: no cover - interface
        raise NotImplementedError


class BaseVisionLanguageRefiner:
    """Model 2: vision-language model to refine labels."""

    async def refine(
        self,
        image: np.ndarray,
        detections: Sequence[DetectionResult],
    ) -> List[DetectionResult]:  # pragma: no cover - interface
        raise NotImplementedError


class BaseHighPrecisionDetector:
    """Model 3: high-precision object detector."""

    async def detect(
        self,
        image: np.ndarray,
        detections: Sequence[DetectionResult],
    ) -> List[DetectionResult]:  # pragma: no cover - interface
        raise NotImplementedError


def merge_detections(
    *detection_sets: Iterable[DetectionResult],
    top_k: int | None = None,
) -> List[DetectionResult]:
    """Merge multiple detection lists, keeping highest confidence per label."""
    merged: dict[str, DetectionResult] = {}

    for det_list in detection_sets:
        for det in det_list:
            existing = merged.get(det.label)
            if existing is None or det.confidence > existing.confidence:
                merged[det.label] = det

    results = sorted(merged.values(), key=lambda d: d.confidence, reverse=True)
    if top_k is not None:
        results = results[:top_k]
    return results


class DetectionService:
    """Runs the three-stage detection pipeline in sequence.

    Pipeline:
      image bytes or PIL.Image
      → preprocessing
      → model1 detection (open vocabulary)
      → model2 label refinement (vision-language)
      → model3 structural detection (high precision)
      → merge outputs
    """

    def __init__(
        self,
        open_vocab_model: BaseOpenVocabularyDetector,
        vl_refiner_model: BaseVisionLanguageRefiner,
        high_precision_model: BaseHighPrecisionDetector,
        target_size: Tuple[int, int] = (640, 640),
        blur_threshold: float = 80.0,
    ) -> None:
        self.open_vocab_model = open_vocab_model
        self.vl_refiner_model = vl_refiner_model
        self.high_precision_model = high_precision_model
        self.target_size = target_size
        self.blur_threshold = blur_threshold

    async def run(
        self,
        image: bytes | "Image.Image",
        top_k: int | None = None,
    ) -> List[dict]:
        """Run the end-to-end detection pipeline and return serializable detections."""
        preprocessed = preprocess_images_for_detection(
            [image],
            target_size=self.target_size,
            blur_threshold=self.blur_threshold,
        )

        if not preprocessed:
            return []

        img_array = preprocessed[0]

        # Model 1: open-vocabulary object detector
        detections_stage1 = await self.open_vocab_model.detect(img_array)

        # Model 2: vision-language label refinement
        detections_stage2 = await self.vl_refiner_model.refine(img_array, detections_stage1)

        # Model 3: high-precision structural detection
        detections_stage3 = await self.high_precision_model.detect(img_array, detections_stage2)

        # Merge outputs from all stages
        merged = merge_detections(detections_stage1, detections_stage2, detections_stage3, top_k=top_k)

        # Normalize labels using synonyms configuration
        normalized = normalize_detections(merged)

        # Convert to simple dicts: {"label": "...", "confidence": 0.xx}
        return [asdict(det) for det in normalized]

