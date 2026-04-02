from __future__ import annotations

from typing import Any

from app.models.schemas import DocumentInput


class MockVlmEngine:
    def run(self, items: list[DocumentInput], prompt: str, max_tokens: int) -> dict[str, Any]:
        outputs = []
        for item in items:
            aspect = round(item.image_width / max(item.image_height, 1), 2)
            outputs.append({
                "document_id": item.document_id,
                "summary": f"Prompt '{prompt}' processed for {item.document_id}; aspect ratio {aspect}, {item.page_count} page(s).",
                "objects": ["document", "text_region", "figure"] if item.image_width > 900 else ["document", "text_region"],
                "max_tokens": max_tokens,
            })
        return {"engine": "mock-vlm", "outputs": outputs}
