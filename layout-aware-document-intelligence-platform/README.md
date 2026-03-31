# Layout-Aware Document Intelligence Platform

This repository is a document parsing system built to handle more than plain text extraction. The goal is to turn messy business documents into deterministic, machine-readable outputs that preserve layout, reading order, sections, tables, and audit history.

Instead of treating a PDF like a blob of OCR text, the system breaks a document into page-level assets, extracts structural blocks, detects tables, applies simple but explicit reading-order rules, validates the output against a typed schema, and stores versioned parse results for later comparison. That makes it a much better foundation for downstream retrieval, review workflows, and agentic automation than a one-shot OCR script.

## What this project does

The platform accepts uploaded PDFs and image-based documents, stores the original file, creates a parse job, and processes the document in a background worker. Each parse produces:

- document metadata
- page images
- layout-aware text blocks
- section hierarchy
- extracted tables
- deterministic entities such as dates, emails, URLs, phone numbers, and money values
- warnings when parsing quality is limited
- revisioned outputs for comparison over time

The current implementation is designed to be practical and easy to run locally while still reflecting the architecture of a production service.

## Why I built it this way

A lot of document pipelines fail in predictable ways:

1. They flatten everything into one string and lose structure.
2. They assume OCR order is the reading order.
3. They do not distinguish paragraphs from headings or tables.
4. They produce free-form output that is hard to validate downstream.
5. They overwrite earlier parses and make debugging impossible.

This repo addresses those problems directly.

- **Layout first:** text is captured with geometry and normalized into block objects.
- **Deterministic reading order:** pages are sorted top-to-bottom with a simple column-aware fallback.
- **Typed outputs:** the final parse is validated with Pydantic models before being saved.
- **Revision history:** every parse is stored as a new revision instead of replacing old results.
- **Debuggability:** page images and structured JSON are saved so failures can be inspected later.

## Repository structure

```text
.
├── app
│   ├── api
│   │   └── routes.py
│   ├── core
│   │   └── config.py
│   ├── db
│   │   ├── base.py
│   │   └── session.py
│   ├── models
│   │   └── document.py
│   ├── schemas
│   │   └── document.py
│   ├── services
│   │   ├── comparison.py
│   │   ├── entities.py
│   │   ├── jobs.py
│   │   ├── layout.py
│   │   ├── ocr.py
│   │   ├── parser.py
│   │   ├── render.py
│   │   ├── storage.py
│   │   └── tables.py
│   ├── utils
│   │   ├── files.py
│   │   └── hashing.py
│   ├── main.py
│   └── worker.py
├── scripts
│   └── create_sample_document.py
├── tests
│   ├── test_comparison.py
│   └── test_layout.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md
```

## Core architecture

### 1. Ingestion

Files are uploaded to the API and persisted under `data/uploads`. The database records the file metadata, content type, size, checksum, and storage path.

### 2. Background job orchestration

Uploading a file creates a queued parse job. A separate worker process polls the database for queued jobs and executes them one by one. This is intentionally simple for local development, but the boundaries are already separated so it is easy to replace with a more scalable queue later.

### 3. Page decomposition

For PDFs, every page is rendered to a PNG artifact. That gives you a stable visual snapshot for debugging and future multimodal extensions.

### 4. Layout extraction

Text is extracted with PyMuPDF as positioned blocks. Each block is normalized into a raw layout object with:

- page number
- bounding box
- extracted text
- estimated font size
- page width and height

### 5. Reading-order logic

Reading order is not taken for granted. The system applies a simple deterministic rule:

- if the page looks effectively single-column, sort by `y` then `x`
- if there is a strong left/right split, order the left column first and the right column second

That is deliberately conservative. It avoids pretending to solve every layout in the world while still doing better than naive text concatenation.

### 6. Table extraction

Tables are extracted with `pdfplumber`. The platform stores the header row, body rows, table geometry, and summary metadata. Text blocks that overlap a detected table region are marked as table-related in the layout layer.

### 7. OCR fallback

If a page has no machine-readable text and Tesseract is available, the worker runs OCR on the rendered page image. The current fallback is intentionally transparent. It records a warning whenever OCR could not be applied.

### 8. Structured outputs and schema validation

Parsed results are assembled into a `DocumentParseResult` object. That schema is validated before the result is written to the database. The final JSON contains:

- `metadata`
- `pages`
- `blocks`
- `sections`
- `tables`
- `entities`
- `warnings`

### 9. Revisioning and comparison

Each parse creates a new revision. The API can compare the latest two revisions and report the delta in page count, block count, sections, tables, entities, and warnings. That makes it easier to track parser regressions or improvements over time.

## Tech stack

- **API:** FastAPI
- **Database:** PostgreSQL in Docker, SQLite fallback for local dev
- **ORM:** SQLAlchemy
- **PDF parsing:** PyMuPDF
- **Table extraction:** pdfplumber
- **OCR fallback:** pytesseract + Tesseract
- **Validation:** Pydantic
- **Containerization:** Docker, Docker Compose
- **Tests:** pytest

## Quick start

### Option A: Local Python setup

1. Create a virtual environment
2. Install dependencies
3. Start the API
4. Start the worker in another terminal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

In a second terminal:

```bash
source .venv/bin/activate
python -m app.worker
```

By default, local development uses SQLite at `./data/app.db`. You can override that with `DATABASE_URL`.

### Option B: Docker Compose

```bash
docker compose up --build
```

That starts:

- the API on port `8000`
- the worker
- PostgreSQL

## Generate a sample document

There is a small script that creates a synthetic utilization-review PDF with a heading, narrative section, and table.

```bash
python scripts/create_sample_document.py
```

Output:

```text
sample_data/sample-insurance-summary.pdf
```

## API walkthrough

### Upload a document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@sample_data/sample-insurance-summary.pdf"
```

Example response:

```json
{
  "document_id": "5c3b0f4a-26ad-4e62-9f30-bcb67eb7bb67",
  "job_id": "44a77cb6-b84c-455f-8d45-91b5678a7de1",
  "status": "queued"
}
```

### Poll the job

```bash
curl http://localhost:8000/jobs/<job_id>
```

### List document revisions

```bash
curl http://localhost:8000/documents/<document_id>/revisions
```

### Fetch a specific revision

```bash
curl http://localhost:8000/documents/<document_id>/revisions/1
```

### Compare the latest two revisions

```bash
curl http://localhost:8000/documents/<document_id>/compare/latest
```

## Example parsed output shape

```json
{
  "metadata": {
    "filename": "sample-insurance-summary.pdf",
    "content_type": "application/pdf",
    "size_bytes": 16231,
    "sha256": "…",
    "page_count": 1,
    "parser_version": "0.1.0",
    "schema_version": "1.0.0",
    "generated_at": "2026-03-30T00:00:00Z",
    "source_type": "pdf"
  },
  "pages": [
    {
      "page_number": 1,
      "width": 595.0,
      "height": 842.0,
      "image_path": "data/artifacts/<document>/v1/page-1.png",
      "block_count": 6,
      "table_count": 1,
      "ocr_used": false
    }
  ],
  "blocks": [
    {
      "id": "p1-b2",
      "page_number": 1,
      "kind": "heading",
      "text": "UTILIZATION REVIEW SUMMARY",
      "bbox": {"x0": 50, "y0": 70, "x1": 260, "y1": 92},
      "reading_order": 2,
      "confidence": 1.0,
      "metadata": {"font_size": 18.0}
    }
  ],
  "sections": [
    {
      "title": "CLINICAL OVERVIEW",
      "level": 1,
      "page_number": 1,
      "block_ids": ["p1-b4", "p1-b5"],
      "summary_text": "The patient presented with persistent knee pain…"
    }
  ],
  "tables": [
    {
      "page_number": 1,
      "bbox": {"x0": 50, "y0": 365, "x1": 490, "y1": 477},
      "columns": ["Service", "Status", "Amount"],
      "rows": [
        ["Orthopedic Consult", "Approved", "$180.00"],
        ["MRI", "Approved", "$1,240.00"],
        ["Surgery", "Pending", "$8,900.00"]
      ],
      "cell_count": 12,
      "source": "pdfplumber",
      "metadata": {"row_count": 3, "column_count": 3}
    }
  ],
  "entities": [
    {"kind": "date", "value": "March 29, 2026", "page_number": 1, "block_id": "p1-b3"},
    {"kind": "money", "value": "$8,900.00", "page_number": 1, "block_id": "p1-b8"}
  ],
  "warnings": []
}
```

## Implementation notes

### Reading order

The reading-order logic here is intentionally explicit and limited. The project is trying to be dependable, not magically universal. If you are dealing with complex magazines, scientific papers, or forms with nested regions, the next step is to add a more sophisticated layout graph or model-assisted reordering layer.

### Tables

`pdfplumber` works best on machine-generated PDFs. For scanned tables, a better production version would pair OCR with table structure detection and cell-line inference.

### OCR

OCR is an escape hatch, not the main pipeline. If Tesseract is missing, the parse still completes, but the warnings field will tell you that a page could not be read.

### Revisioning

The first parse creates version `1`. Any reparse creates version `2`, `3`, and so on. That is useful when you improve extraction logic or compare OCR settings.

## Running tests

```bash
pytest
```

The included tests cover:

- column-aware reading order
- heading-to-section inference
- revision summary comparison logic

## Design tradeoffs

I chose to keep the first implementation focused and inspectable.

- The queue is database-polled instead of using Kafka or Celery.
- OCR fallback is synchronous and page-level.
- Section inference is heuristic rather than model-based.
- Entity extraction is regex-based for determinism.
- Local development supports SQLite, but Docker uses PostgreSQL because that is closer to a real deployment.

These choices make the system easier to run and extend without hiding the core architecture behind too much scaffolding.


## Reference implementation choices

This build leans on FastAPI for the API layer, PyMuPDF for positioned text extraction, and pdfplumber for tables. FastAPI’s official docs position it as a high-performance Python API framework, PyMuPDF documents `Page.get_text("blocks")` and sorted text extraction for ordering-aware parsing, and pdfplumber’s project documentation emphasizes detailed PDF structure access plus table extraction. citeturn810702search3turn810702search1turn810702search4turn810702search2

## License

MIT
