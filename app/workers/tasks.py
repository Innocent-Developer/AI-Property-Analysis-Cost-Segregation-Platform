from __future__ import annotations

import asyncio
import uuid
from typing import List

from celery import chain
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.detection_service import (
    BaseHighPrecisionDetector,
    BaseOpenVocabularyDetector,
    BaseVisionLanguageRefiner,
    DetectionResult,
    DetectionService,
)
from app.database.session import AsyncSessionLocal
from app.financial_engine.engine import AssetInput, compute_financial_breakdown
from app.models.property import Detection, Image, Property, Report
from app.report_generator.excel_report import generate_excel_report
from app.rules_engine.deduplication import deduplicate_assets
from app.rules_engine.rules_engine import classify_detections
from app.workers.celery_app import celery


class DummyOpenVocabularyDetector(BaseOpenVocabularyDetector):
    async def detect(self, image) -> List[DetectionResult]:
        # Placeholder – replace with real model inference
        return []


class DummyVisionLanguageRefiner(BaseVisionLanguageRefiner):
    async def refine(self, image, detections: List[DetectionResult]) -> List[DetectionResult]:
        return detections


class DummyHighPrecisionDetector(BaseHighPrecisionDetector):
    async def detect(self, image, detections: List[DetectionResult]) -> List[DetectionResult]:
        return detections


def _create_detection_service() -> DetectionService:
    return DetectionService(
        open_vocab_model=DummyOpenVocabularyDetector(),
        vl_refiner_model=DummyVisionLanguageRefiner(),
        high_precision_model=DummyHighPrecisionDetector(),
    )


async def _run_ai_detection_for_property(session: AsyncSession, property_id: uuid.UUID) -> None:
    service = _create_detection_service()

    images = (
        await session.execute(select(Image).where(Image.property_id == property_id))
    ).scalars().all()

    for img in images:
        # Load raw image bytes from storage
        # The stored URL is relative (/storage/properties/{property_id}/{filename});
        # application code can adapt this to a filesystem path.
        # Here we only demonstrate the pipeline invocation pattern.
        detections = await service.run(image=b"", top_k=None)  # placeholder

        for det in detections:
            detection_row = Detection(
                image_id=img.id,
                label=det["label"],
                confidence=det["confidence"],
                normalized_label=det["label"],
            )
            session.add(detection_row)

    await session.commit()


async def _generate_report_for_property(session: AsyncSession, property_id: uuid.UUID) -> str:
    property_obj = await session.get(Property, property_id)
    if not property_obj:
        return ""

    detections = (
        await session.execute(
            select(Detection).join(Image).where(Image.property_id == property_id)
        )
    ).scalars().all()

    detection_results = [DetectionResult(label=d.label, confidence=d.confidence) for d in detections]

    # Normalize and classify detections into assets
    asset_classifications = classify_detections(detection_results)

    # Deduplicate into asset counts (1 per asset type in this example)
    labels = [ac.normalized_label for ac in asset_classifications]
    deduped = deduplicate_assets(labels)

    assets_inputs = [
        AssetInput(name=label, quantity=count, unit_replacement_cost=1) for label, count in deduped
    ]

    improvement_basis = property_obj.improvement_basis or 0
    financial_breakdown = compute_financial_breakdown(assets_inputs, improvement_basis=improvement_basis)

    property_info = {
        "id": str(property_obj.id),
        "address": property_obj.address,
        "property_type": property_obj.property_type,
        "improvement_basis": property_obj.improvement_basis,
        "created_at": property_obj.created_at,
    }

    report_path = generate_excel_report(
        property_info=property_info,
        asset_classifications=asset_classifications,
        financial_breakdown=financial_breakdown,
    )

    report = Report(property_id=property_obj.id, report_url=str(report_path))
    session.add(report)
    await session.commit()

    return str(report_path)


@celery.task(name="image_processing.enqueue", queue="image_processing")
def enqueue_full_pipeline(property_id: str) -> None:
    """Entry point when images are uploaded.

    Kicks off the full pipeline on background queues:
      image_processing → ai_detection → report_generation
    """
    chain(
        run_ai_detection_task.s(property_id).set(queue="ai_detection"),
        generate_report_task.s().set(queue="report_generation"),
    ).apply_async()


@celery.task(name="ai_detection.run", queue="ai_detection")
def run_ai_detection_task(property_id: str) -> str:
    async def _inner() -> str:
        async with AsyncSessionLocal() as session:
            await _run_ai_detection_for_property(session, uuid.UUID(property_id))
        return property_id

    return asyncio.run(_inner())


@celery.task(name="report_generation.generate", queue="report_generation")
def generate_report_task(property_id: str) -> str:
    async def _inner() -> str:
        async with AsyncSessionLocal() as session:
            return await _generate_report_for_property(session, uuid.UUID(property_id))

    return asyncio.run(_inner())

