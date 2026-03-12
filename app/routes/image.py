import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.property import ImageResponse
from app.services.image_service import upload_property_images
from app.workers.tasks import enqueue_full_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["images"])


@router.post(
    "/property/{property_id}/images",
    response_model=List[ImageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_images_for_property(
    property_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> List[ImageResponse]:
    try:
        images = await upload_property_images(db, property_id, files)
    except ValueError as exc:
        # Property not found or invalid image format/data
        detail = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "Property not found" in detail else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=detail)

    # Enqueue pipeline in a thread so the request returns immediately (avoids blocking on Redis)
    def _enqueue():
        try:
            enqueue_full_pipeline.delay(str(property_id))
        except Exception as exc:
            logger.warning("Celery/Redis unavailable, pipeline not enqueued: %s", exc)

    _executor = getattr(upload_images_for_property, "_executor", None)
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="celery_enqueue")
        upload_images_for_property._executor = _executor  # type: ignore[attr-defined]
    _executor.submit(_enqueue)

    return [ImageResponse.model_validate(img) for img in images]

