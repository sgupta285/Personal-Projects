
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Iterable

from app.schemas.document import BoundingBox, DocumentSection, LayoutBlock


@dataclass
class RawTextBlock:
    id: str
    page_number: int
    text: str
    bbox: tuple[float, float, float, float]
    font_size: float
    page_width: float
    page_height: float


def _column_bucket(block: RawTextBlock) -> int:
    center_x = (block.bbox[0] + block.bbox[2]) / 2
    return 0 if center_x < (block.page_width / 2) else 1


def reading_order(blocks: Iterable[RawTextBlock]) -> list[RawTextBlock]:
    block_list = [block for block in blocks if block.text.strip()]
    if not block_list:
        return []
    left = [block for block in block_list if _column_bucket(block) == 0]
    right = [block for block in block_list if _column_bucket(block) == 1]
    split_columns = left and right and abs(len(left) - len(right)) <= len(block_list)
    if split_columns:
        return sorted(left, key=lambda item: (item.bbox[1], item.bbox[0])) + sorted(
            right,
            key=lambda item: (item.bbox[1], item.bbox[0]),
        )
    return sorted(block_list, key=lambda item: (item.bbox[1], item.bbox[0]))


def classify_blocks(raw_blocks: list[RawTextBlock], table_regions: dict[int, list[tuple[float, float, float, float]]]) -> list[LayoutBlock]:
    if not raw_blocks:
        return []

    font_sizes = [block.font_size for block in raw_blocks if block.font_size > 0]
    median_font = statistics.median(font_sizes) if font_sizes else 11.0

    ordered = reading_order(raw_blocks)
    layout_blocks: list[LayoutBlock] = []

    for order, block in enumerate(ordered, start=1):
        x0, y0, x1, y1 = block.bbox
        kind = "paragraph"
        text = block.text.strip()

        if y0 < 60:
            kind = "header"
        elif y1 > block.page_height - 50:
            kind = "footer"
        elif _overlaps_table(block.bbox, table_regions.get(block.page_number, [])):
            kind = "table"
        elif block.font_size >= median_font + 1.5 and len(text) <= 120:
            kind = "heading"
        elif text.isupper() and len(text) <= 90:
            kind = "heading"

        layout_blocks.append(
            LayoutBlock(
                id=block.id,
                page_number=block.page_number,
                kind=kind,
                text=text,
                bbox=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
                reading_order=order,
                confidence=1.0,
                metadata={"font_size": block.font_size},
            )
        )
    return layout_blocks


def infer_sections(blocks: list[LayoutBlock]) -> list[DocumentSection]:
    sections: list[DocumentSection] = []
    current: DocumentSection | None = None
    for block in blocks:
        if block.kind == "heading":
            level = 1 if block.metadata.get("font_size", 0) >= 14 else 2
            current = DocumentSection(
                title=block.text,
                level=level,
                page_number=block.page_number,
                block_ids=[block.id],
                summary_text="",
            )
            sections.append(current)
        elif current and block.kind in {"paragraph", "table"}:
            current.block_ids.append(block.id)
            snippet = block.text[:180]
            if snippet and len(current.summary_text) < 600:
                current.summary_text = (current.summary_text + " " + snippet).strip()
    return sections


def _overlaps_table(
    bbox: tuple[float, float, float, float],
    table_regions: list[tuple[float, float, float, float]],
) -> bool:
    for tx0, ty0, tx1, ty1 in table_regions:
        ix0 = max(bbox[0], tx0)
        iy0 = max(bbox[1], ty0)
        ix1 = min(bbox[2], tx1)
        iy1 = min(bbox[3], ty1)
        if ix1 > ix0 and iy1 > iy0:
            return True
    return False
