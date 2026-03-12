import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.detection_service import DetectionResult
from app.database.session import get_db
from app.financial_engine.engine import AssetInput, compute_financial_breakdown
from app.models.property import Detection, Image, Property, Report
from app.report_generator.excel_report import generate_excel_report
from app.rules_engine.deduplication import deduplicate_assets
from app.rules_engine.rules_engine import classify_detections
from app.workers.tasks import _create_detection_service


router = APIRouter(tags=["analysis"])


def _image_path_from_url(url: str) -> Path:
    # image_url stored as /storage/properties/{property_id}/{filename}
    # Map it to the filesystem under project root.
    project_root = Path(__file__).resolve().parents[2]
    return project_root / url.lstrip("/")


@router.post("/analyze-property/{property_id}", summary="Run full property analysis")
async def analyze_property(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # 1. Get property
    property_obj = await db.get(Property, property_id)
    if not property_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # 1. Get property images
    images = (
        await db.execute(select(Image).where(Image.property_id == property_id))
    ).scalars().all()
    if not images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No images found for property")

    service = _create_detection_service()
    all_detections: List[DetectionResult] = []

    # 2–4. Preprocess images, run AI detection, normalize labels (handled inside DetectionService)
    for img in images:
        img_path = _image_path_from_url(img.image_url)
        if not img_path.exists():
            continue
        image_bytes = img_path.read_bytes()
        detections = await service.run(image=image_bytes, top_k=None)

        for det in detections:
            det_result = DetectionResult(label=det["label"], confidence=det["confidence"])
            all_detections.append(det_result)

            # 3/4. Store detections with normalized labels
            detection_row = Detection(
                image_id=img.id,
                label=det_result.label,
                confidence=det_result.confidence,
                normalized_label=det_result.label,
            )
            db.add(detection_row)

    await db.commit()

    if not all_detections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No detections produced for property images")

    # 5. Deduplicate detections
    labels = [d.label for d in all_detections]
    deduped = deduplicate_assets(labels)

    # 6. Classify assets
    asset_classifications = classify_detections(all_detections)

    # 7. Run financial calculations
    assets_inputs = [
        AssetInput(name=label, quantity=count, unit_replacement_cost=1) for label, count in deduped
    ]
    improvement_basis = property_obj.improvement_basis or 0
    financial_breakdown = compute_financial_breakdown(assets_inputs, improvement_basis=improvement_basis)

    # 8–9. Generate Excel report and store report row
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
    db.add(report)
    await db.commit()

    # 10. Return report URL
    return {"report_url": str(report_path)}

