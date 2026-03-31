
from __future__ import annotations

import shutil
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

from app.core.config import settings


def ocr_available() -> bool:
    return bool(
        settings.enable_ocr_fallback
        and pytesseract is not None
        and Image is not None
        and shutil.which(settings.tesseract_cmd)
    )


def run_ocr(image_path: Path) -> str:
    if not ocr_available():
        return ""
    return pytesseract.image_to_string(Image.open(image_path))
