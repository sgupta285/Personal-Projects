
from __future__ import annotations

from pathlib import Path

import fitz


def render_pdf_pages(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    rendered_paths: list[Path] = []
    document = fitz.open(pdf_path)
    try:
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            target = output_dir / f"page-{page_index + 1}.png"
            pix.save(target.as_posix())
            rendered_paths.append(target)
    finally:
        document.close()
    return rendered_paths
