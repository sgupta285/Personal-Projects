
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class LayoutBlock(BaseModel):
    id: str
    page_number: int
    kind: Literal["header", "footer", "heading", "paragraph", "table", "figure", "ocr_text"]
    text: str = ""
    bbox: BoundingBox
    reading_order: int
    confidence: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class TableCell(BaseModel):
    row_index: int
    col_index: int
    value: str


class TableData(BaseModel):
    page_number: int
    bbox: BoundingBox | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    cell_count: int
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentSection(BaseModel):
    title: str
    level: int
    page_number: int
    block_ids: list[str] = Field(default_factory=list)
    summary_text: str = ""


class ExtractedEntity(BaseModel):
    kind: Literal["email", "phone", "date", "money", "url"]
    value: str
    page_number: int
    block_id: str | None = None


class ParseMetadata(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    page_count: int
    parser_version: str
    schema_version: str
    generated_at: datetime
    source_type: Literal["pdf", "image", "other"]


class PageSummary(BaseModel):
    page_number: int
    width: float
    height: float
    image_path: str | None = None
    block_count: int
    table_count: int
    ocr_used: bool = False


class DocumentParseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: ParseMetadata
    pages: list[PageSummary]
    blocks: list[LayoutBlock]
    sections: list[DocumentSection]
    tables: list[TableData]
    entities: list[ExtractedEntity]
    warnings: list[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    document_id: str
    job_id: str
    status: str


class JobResponse(BaseModel):
    id: str
    document_id: str
    status: str
    error_message: str | None = None
    requested_by: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: datetime
    latest_version: int | None = None


class RevisionResponse(BaseModel):
    id: str
    document_id: str
    version: int
    schema_version: str
    summary_json: dict[str, Any]
    created_at: datetime


class RevisionCompareResponse(BaseModel):
    document_id: str
    from_version: int
    to_version: int
    changes: dict[str, Any]
