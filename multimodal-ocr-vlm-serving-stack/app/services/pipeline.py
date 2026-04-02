from __future__ import annotations

from typing import Any

from app.models.schemas import DocumentInput
from app.services.ocr import MockOcrEngine
from app.services.vlm import MockVlmEngine


class PipelineService:
    def __init__(self):
        self.ocr = MockOcrEngine()
        self.vlm = MockVlmEngine()

    def run(self, items: list[DocumentInput], prompt: str, language: str) -> dict[str, Any]:
        ocr = self.ocr.run(items, language=language, use_layout=True)
        vlm = self.vlm.run(items, prompt=prompt, max_tokens=160)
        merged = []
        for doc, vision in zip(ocr['documents'], vlm['outputs']):
            merged.append({
                'document_id': doc['document_id'],
                'text': doc['text'],
                'layout': doc['layout'],
                'vision_summary': vision['summary'],
                'entities': [
                    {'type': 'document_id', 'value': doc['document_id']},
                    {'type': 'table_count', 'value': doc['layout']['tables']},
                ],
            })
        return {'engine': 'mock-pipeline', 'documents': merged}
