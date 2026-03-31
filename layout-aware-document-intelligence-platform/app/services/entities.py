
from __future__ import annotations

import re

from app.schemas.document import ExtractedEntity, LayoutBlock

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?\d{1,2}\s*)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Z][a-z]{2,8}\s+\d{1,2},\s+\d{4})\b")
MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")
URL_RE = re.compile(r"\bhttps?://[^\s]+\b")


def extract_entities(blocks: list[LayoutBlock]) -> list[ExtractedEntity]:
    entities: list[ExtractedEntity] = []
    patterns = {
        "email": EMAIL_RE,
        "phone": PHONE_RE,
        "date": DATE_RE,
        "money": MONEY_RE,
        "url": URL_RE,
    }
    for block in blocks:
        for kind, pattern in patterns.items():
            for match in pattern.finditer(block.text):
                entities.append(
                    ExtractedEntity(
                        kind=kind,
                        value=match.group(0),
                        page_number=block.page_number,
                        block_id=block.id,
                    )
                )
    return entities
