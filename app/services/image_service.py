import io
import os
import uuid
from pathlib import Path
from typing import Iterable, List

from fastapi import UploadFile
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Image as ImageModel
from app.models.property import Property


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE = (1920, 1080)


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def _validate_image_file(file: UploadFile) -> None:
    ext = _get_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported image format. Allowed: jpg, jpeg, png, webp.")


def _storage_directory(property_id: uuid.UUID) -> Path:
    # project_root/app/services/image_service.py -> project_root
    project_root = Path(__file__).resolve().parents[2]
    storage_dir = project_root / "storage" / "properties" / str(property_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


async def upload_property_images(
    db: AsyncSession,
    property_id: uuid.UUID,
    files: Iterable[UploadFile],
) -> List[ImageModel]:
    # Ensure property exists
    result = await db.execute(select(Property).where(Property.id == property_id))
    if result.scalar_one_or_none() is None:
        raise ValueError("Property not found.")

    storage_dir = _storage_directory(property_id)
    saved_images: list[ImageModel] = []

    for file in files:
        _validate_image_file(file)
        raw_bytes = await file.read()

        try:
            pil_image = Image.open(io.BytesIO(raw_bytes))
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid image data.") from exc

        pil_image = pil_image.convert("RGB")
        pil_image.thumbnail(MAX_SIZE)

        ext = _get_extension(file.filename or "") or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = storage_dir / filename

        pil_image.save(file_path, optimize=True, quality=85)

        # URL path (relative to API root); mounting /storage as static is optional
        url_path = f"/storage/properties/{property_id}/{filename}"

        image_row = ImageModel(property_id=property_id, image_url=url_path)
        db.add(image_row)
        saved_images.append(image_row)

    await db.commit()
    for image in saved_images:
        await db.refresh(image)

    return saved_images

