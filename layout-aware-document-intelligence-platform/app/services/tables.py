
from __future__ import annotations

from pathlib import Path

import pdfplumber

from app.schemas.document import BoundingBox, TableData


def extract_tables(pdf_path: Path) -> tuple[list[TableData], dict[int, list[tuple[float, float, float, float]]]]:
    tables: list[TableData] = []
    table_regions: dict[int, list[tuple[float, float, float, float]]] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            regions: list[tuple[float, float, float, float]] = []
            found_tables = page.find_tables()
            for found in found_tables:
                rows = found.extract() or []
                if not rows:
                    continue
                header = [str(cell or "").strip() for cell in rows[0]]
                body = [[str(cell or "").strip() for cell in row] for row in rows[1:]]
                bbox = tuple(float(v) for v in found.bbox)
                regions.append(bbox)
                cell_count = sum(len(row) for row in rows)
                tables.append(
                    TableData(
                        page_number=page_index,
                        bbox=BoundingBox(x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3]),
                        columns=header,
                        rows=body,
                        cell_count=cell_count,
                        source="pdfplumber",
                        metadata={"row_count": len(body), "column_count": len(header)},
                    )
                )
            if regions:
                table_regions[page_index] = regions

    return tables, table_regions
