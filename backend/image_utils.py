"""Procesamiento de imágenes: crop center 16:10 → 800x500 → WebP."""

import io
import os
import uuid

from PIL import Image

from config import get_settings

TARGET_SIZE = (800, 500)
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}


class InvalidImage(Exception):
    pass


def process_upload(file_bytes: bytes, content_type: str) -> str:
    """Valida, recorta al centro en 16:10, redimensiona a 800x500 y guarda WebP."""
    if not content_type or content_type.split(";")[0].strip().lower() not in ALLOWED_TYPES:
        raise InvalidImage("Formato no soportado (usá JPG, PNG, WebP, GIF o BMP)")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise InvalidImage("La imagen supera los 5 MB")

    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.load()
    except Exception as exc:
        raise InvalidImage("No se pudo leer la imagen") from exc

    img = img.convert("RGB")

    w, h = img.size
    target_ratio = TARGET_SIZE[0] / TARGET_SIZE[1]
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    filename = f"{uuid.uuid4().hex}.webp"
    upload_dir = get_settings().upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    img.save(os.path.join(upload_dir, filename), "WEBP", quality=85)
    return f"/uploads/{filename}"
