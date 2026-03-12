from __future__ import annotations

import io
from typing import Iterable, List, Tuple

import cv2
import numpy as np
from PIL import Image, ImageFilter


def _to_pil(image: bytes | Image.Image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    return Image.open(io.BytesIO(image))


def _pil_to_ndarray_rgb(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("RGB"))


def resize_image(
    image: bytes | Image.Image,
    size: Tuple[int, int] = (640, 640),
    keep_aspect_ratio: bool = True,
) -> np.ndarray:
    """Resize image for downstream AI models, returning RGB ndarray."""
    pil_img = _to_pil(image)

    if keep_aspect_ratio:
        pil_img.thumbnail(size, Image.LANCZOS)
        canvas = Image.new("RGB", size, (0, 0, 0))
        offset_x = (size[0] - pil_img.width) // 2
        offset_y = (size[1] - pil_img.height) // 2
        canvas.paste(pil_img, (offset_x, offset_y))
        pil_img = canvas
    else:
        pil_img = pil_img.resize(size, Image.LANCZOS)

    return _pil_to_ndarray_rgb(pil_img)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image pixels to float32 in [0, 1] RGB."""
    if image.dtype != np.float32:
        image = image.astype(np.float32)
    image /= 255.0
    return image


def remove_low_quality_images(
    images: Iterable[np.ndarray],
    blur_threshold: float = 80.0,
) -> List[np.ndarray]:
    """Filter out low-quality images using Laplacian variance (blur detection)."""
    kept: list[np.ndarray] = []

    for img in images:
        if img.ndim == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm >= blur_threshold:
            kept.append(img)

    return kept


def extract_image_metadata(image: bytes | Image.Image) -> dict:
    """Extract basic metadata from an image (size, mode, format, EXIF where available)."""
    pil_img = _to_pil(image)

    width, height = pil_img.size
    metadata: dict = {
        "width": width,
        "height": height,
        "mode": pil_img.mode,
        "format": pil_img.format,
    }

    try:
        exif = pil_img.getexif()
        if exif:
            # Keep simple numeric key/value EXIF; real systems might map tags.
            metadata["exif"] = {int(k): exif.get(k) for k in exif.keys()}
    except Exception:
        # Some formats won't provide EXIF; safely ignore.
        pass

    return metadata


def preprocess_images_for_detection(
    images: Iterable[bytes | Image.Image],
    target_size: Tuple[int, int] = (640, 640),
    blur_threshold: float = 80.0,
) -> List[np.ndarray]:
    """Full preprocessing pipeline: resize, normalize, and filter low-quality images."""
    resized = [resize_image(img, size=target_size) for img in images]
    filtered = remove_low_quality_images(resized, blur_threshold=blur_threshold)
    normalized = [normalize_image(img) for img in filtered]
    return normalized

