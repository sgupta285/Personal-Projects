
from __future__ import annotations

import mimetypes
from pathlib import Path


def guess_content_type(filename: str) -> str:
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def safe_filename(name: str) -> str:
    return "".join(char if char.isalnum() or char in {".", "-", "_"} else "_" for char in name)
