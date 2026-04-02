from __future__ import annotations

from typing import Any

from app.models.schemas import DocumentInput


class MockOcrEngine:
    def run(self, items: list[DocumentInput], language: str, use_layout: bool) -> dict[str, Any]:
        pages = []
        for item in items:
            text = item.text_hint or f"Detected text for {item.document_id}"
            layout = {
                "blocks": max(1, item.page_count * 3),
                "tables": 1 if use_layout and item.image_width > 1000 else 0,
                "language": language,
            }
            pages.append({
                "document_id": item.document_id,
                "page_count": item.page_count,
                "text": text,
                "layout": layout,
            })
        return {"engine": "mock-ocr", "documents": pages}
