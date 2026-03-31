
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz

from app.core.config import settings
from app.schemas.document import (
    BoundingBox,
    DocumentParseResult,
    LayoutBlock,
    PageSummary,
    ParseMetadata,
)
from app.services.entities import extract_entities
from app.services.layout import RawTextBlock, classify_blocks, infer_sections
from app.services.ocr import ocr_available, run_ocr
from app.services.render import render_pdf_pages
from app.services.tables import extract_tables
from app.utils.hashing import sha256_file


class DocumentParser:
    parser_version = "0.1.0"

    def parse(self, path: Path, filename: str, content_type: str, artifact_dir: Path) -> DocumentParseResult:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(path, filename, content_type, artifact_dir)
        return self._parse_image_or_other(path, filename, content_type, artifact_dir)

    def _parse_pdf(self, path: Path, filename: str, content_type: str, artifact_dir: Path) -> DocumentParseResult:
        warnings: list[str] = []
        tables, table_regions = extract_tables(path)
        rendered_images = render_pdf_pages(path, artifact_dir)
        document = fitz.open(path)
        try:
            raw_blocks: list[RawTextBlock] = []
            pages: list[PageSummary] = []

            for page_index in range(document.page_count):
                page_number = page_index + 1
                page = document.load_page(page_index)
                page_dict = page.get_text("dict", sort=True)
                width = float(page.rect.width)
                height = float(page.rect.height)

                page_block_count = 0
                for block_idx, block in enumerate(page_dict.get("blocks", []), start=1):
                    if block.get("type") != 0:
                        continue
                    bbox = tuple(float(v) for v in block.get("bbox", (0, 0, 0, 0)))
                    lines = block.get("lines", [])
                    text_parts: list[str] = []
                    font_sizes: list[float] = []
                    for line in lines:
                        for span in line.get("spans", []):
                            span_text = str(span.get("text", "")).strip()
                            if span_text:
                                text_parts.append(span_text)
                                font_sizes.append(float(span.get("size", 0)))
                    text = " ".join(text_parts).strip()
                    if not text:
                        continue
                    font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 11.0
                    raw_blocks.append(
                        RawTextBlock(
                            id=f"p{page_number}-b{block_idx}",
                            page_number=page_number,
                            text=text,
                            bbox=bbox,
                            font_size=font_size,
                            page_width=width,
                            page_height=height,
                        )
                    )
                    page_block_count += 1

                ocr_used = False
                if page_block_count == 0 and ocr_available():
                    ocr_text = run_ocr(rendered_images[page_index])
                    if ocr_text.strip():
                        raw_blocks.append(
                            RawTextBlock(
                                id=f"p{page_number}-ocr-1",
                                page_number=page_number,
                                text=ocr_text,
                                bbox=(0.0, 0.0, width, height),
                                font_size=11.0,
                                page_width=width,
                                page_height=height,
                            )
                        )
                        page_block_count = 1
                        ocr_used = True
                elif page_block_count == 0:
                    warnings.append(
                        f"Page {page_number} had no machine-readable text and OCR fallback was unavailable."
                    )

                pages.append(
                    PageSummary(
                        page_number=page_number,
                        width=width,
                        height=height,
                        image_path=str(rendered_images[page_index]),
                        block_count=page_block_count,
                        table_count=len([table for table in tables if table.page_number == page_number]),
                        ocr_used=ocr_used,
                    )
                )
        finally:
            document.close()

        blocks = classify_blocks(raw_blocks, table_regions)
        if ocr_available():
            for block in blocks:
                if block.id.endswith("-ocr-1"):
                    block.kind = "ocr_text"

        sections = infer_sections(blocks)
        entities = extract_entities(blocks)

        metadata = ParseMetadata(
            filename=filename,
            content_type=content_type,
            size_bytes=path.stat().st_size,
            sha256=sha256_file(path),
            page_count=len(pages),
            parser_version=self.parser_version,
            schema_version=settings.schema_version,
            generated_at=datetime.now(timezone.utc),
            source_type="pdf",
        )
        return DocumentParseResult(
            metadata=metadata,
            pages=pages,
            blocks=blocks,
            sections=sections,
            tables=tables,
            entities=entities,
            warnings=warnings,
        )

    def _parse_image_or_other(self, path: Path, filename: str, content_type: str, artifact_dir: Path) -> DocumentParseResult:
        warnings: list[str] = []
        blocks: list[LayoutBlock] = []
        pages = [
            PageSummary(
                page_number=1,
                width=0,
                height=0,
                image_path=str(path),
                block_count=0,
                table_count=0,
                ocr_used=False,
            )
        ]

        if ocr_available():
            text = run_ocr(path)
            if text.strip():
                blocks.append(
                    LayoutBlock(
                        id="p1-ocr-1",
                        page_number=1,
                        kind="ocr_text",
                        text=text.strip(),
                        bbox=BoundingBox(x0=0, y0=0, x1=0, y1=0),
                        reading_order=1,
                        confidence=0.8,
                        metadata={},
                    )
                )
                pages[0].block_count = 1
                pages[0].ocr_used = True
        else:
            warnings.append("OCR fallback is not available for non-PDF documents.")

        metadata = ParseMetadata(
            filename=filename,
            content_type=content_type,
            size_bytes=path.stat().st_size,
            sha256=sha256_file(path),
            page_count=1,
            parser_version=self.parser_version,
            schema_version=settings.schema_version,
            generated_at=datetime.now(timezone.utc),
            source_type="image" if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff"} else "other",
        )

        sections = infer_sections(blocks)
        entities = extract_entities(blocks)

        return DocumentParseResult(
            metadata=metadata,
            pages=pages,
            blocks=blocks,
            sections=sections,
            tables=[],
            entities=entities,
            warnings=warnings,
        )
