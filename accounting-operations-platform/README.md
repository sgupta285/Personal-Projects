# Accounting Operations Platform

A GitHub-ready accounting operations platform focused on invoice intake, approval workflows, vendor management, payment tracking, auditability, and operator visibility. The repo is intentionally designed to look like a practical internal tool a finance-ops or shared-services team would actually use.

This project is one of the domain variants from your broader project list. Instead of treating it as a thin rebrand, this implementation turns the underlying workflow ideas into a real accounting-focused product with traceable invoice state changes, approval decisions, payment scheduling, reconciliation support, and operations reporting.

## Why this project exists

Finance and accounting teams often operate across disconnected tools: inboxes for invoice intake, spreadsheets for approvals, ERP systems for payments, and chat or email for exceptions. That fragmentation creates duplicated work, weak audit trails, slow approvals, and poor visibility into liabilities.

This repo demonstrates how to build an operational layer that sits between raw invoice intake and downstream payment execution. It captures invoice metadata, routes approvals, records every material action, tracks payment status, and exposes the workflow through clean APIs and a lightweight frontend.

## What the platform does

- stores vendor records and invoice metadata
- supports invoice creation from manual entry or CSV ingestion
- validates duplicates based on vendor invoice number
- manages approval workflows with finance-review and manager-approval stages
- records approval, rejection, hold, and payment events in an audit log
- tracks invoice lifecycle from intake to payment
- provides aging and liability summaries for operators
- exposes a simple web console scaffold for finance users
- packages the entire repo in a clean structure suitable for GitHub

## Primary workflow

1. A finance operator creates or imports a vendor invoice.
2. The platform validates required fields and checks for duplicates.
3. The invoice starts in `pending_review`.
4. A reviewer can approve, reject, or place it on hold.
5. After approval, accounting can mark it as `approved` and then `scheduled_for_payment`.
6. Once remittance happens, the invoice is marked `paid`.
7. Every state transition is written to the audit trail.

## Product features

### 1. Vendor management
- create and list vendors
- track contact email and payment terms
- link invoices to a single canonical vendor record

### 2. Invoice intake
- create invoices through the API
- bulk import invoices from CSV
- attach freeform notes
- preserve vendor invoice number for duplicate checks

### 3. Workflow and approvals
- finance review action
- manager approval action
- rejection and hold support
- optional notes per action

### 4. Payment tracking
- schedule invoices for payment
- mark invoices as paid
- store payment reference, method, and payment date

### 5. Auditability
- capture all workflow events with actor, timestamp, and notes
- preserve immutable invoice-event history

### 6. Reporting
- invoice aging summary
- outstanding liability view
- approval throughput metrics
- vendor-level invoice breakdown

## Repo structure

```text
accounting-operations-platform/
├── backend/
│   ├── app/
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── data/
│   │   └── sample_invoices.csv
│   ├── tests/
│   │   └── test_workflow.py
│   ├── requirements.txt
│   └── seed.py
├── docs/
│   └── architecture.md
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       └── components/
│           ├── InvoiceTable.tsx
│           └── MetricCard.tsx
├── scripts/
│   ├── run_backend.sh
│   └── smoke_test.py
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

## Backend architecture

The backend uses FastAPI as the HTTP layer and SQLite for local persistence through the standard-library `sqlite3` module. This keeps the repo easy to run while still modeling realistic production concepts:

- `db.py` initializes tables and connections
- `repository.py` contains all SQL access
- `services.py` contains business rules and workflow transitions
- `schemas.py` defines request and response contracts
- `main.py` wires the API routes and reporting endpoints

For production, the same design can be moved to PostgreSQL with minimal repository changes.

## Data model

### vendors
- `id`
- `name`
- `contact_email`
- `payment_terms_days`
- `created_at`

### invoices
- `id`
- `vendor_id`
- `vendor_invoice_number`
- `invoice_date`
- `due_date`
- `currency`
- `amount`
- `status`
- `description`
- `notes`
- `created_at`
- `updated_at`

### payments
- `id`
- `invoice_id`
- `payment_reference`
- `payment_method`
- `payment_date`
- `amount_paid`
- `created_at`

### audit_events
- `id`
- `invoice_id`
- `actor`
- `event_type`
- `notes`
- `created_at`

## Status model

Supported invoice statuses:

- `pending_review`
- `on_hold`
- `rejected`
- `approved`
- `scheduled_for_payment`
- `paid`

## API overview

### Health
- `GET /health`

### Vendors
- `POST /vendors`
- `GET /vendors`

### Invoices
- `POST /invoices`
- `GET /invoices`
- `GET /invoices/{invoice_id}`
- `POST /invoices/import-csv`

### Workflow
- `POST /invoices/{invoice_id}/approve`
- `POST /invoices/{invoice_id}/hold`
- `POST /invoices/{invoice_id}/reject`
- `POST /invoices/{invoice_id}/schedule-payment`
- `POST /invoices/{invoice_id}/mark-paid`

### Reporting
- `GET /reports/aging`
- `GET /reports/liabilities`
- `GET /reports/vendors/{vendor_id}`

## Local development

### 1. Create a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Seed example data

```bash
python seed.py
```

### 4. Start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

## CSV import format

Expected headers:

```csv
vendor_name,vendor_email,payment_terms_days,vendor_invoice_number,invoice_date,due_date,currency,amount,description,notes
```

A sample file is provided in `backend/data/sample_invoices.csv`.

## Make targets

```bash
make test           # run backend tests
make smoke          # run a local smoke workflow without starting the API
make seed           # seed sample data
make backend        # start the FastAPI service
```

## Docker

Run everything with Docker Compose:

```bash
docker compose up --build
```

This starts the FastAPI backend and serves the frontend dev scaffold in a containerized flow.

## Example operator scenarios

### Scenario 1: Intake a new invoice
- create vendor if missing
- post invoice
- review dashboard shows it under pending review

### Scenario 2: Place invoice on hold
- reviewer notices missing PO or wrong coding
- move invoice to `on_hold`
- audit note captures why it was blocked

### Scenario 3: Approve and pay
- reviewer approves invoice
- accounting schedules payment
- treasury marks it paid with ACH reference
- liabilities report updates automatically

## Testing strategy

The backend test suite focuses on the parts that matter most for credibility:

- vendor creation
- duplicate invoice prevention
- workflow transitions
- payment lifecycle correctness
- aging and liability report behavior

## Design decisions

### Why SQLite instead of PostgreSQL in the repo
This repo is meant to be easy to clone and run immediately. SQLite keeps setup friction low while still demonstrating a realistic operational design.

### Why standard-library SQL instead of an ORM
For a project like this, explicit repository methods keep business logic easy to follow and make the code feel grounded and practical.

### Why include a frontend scaffold
Even internal tools benefit from a visible operator surface. A lightweight React dashboard makes the repo feel like a full product rather than an API-only prototype.

## How this would evolve in production

- replace SQLite with PostgreSQL
- add S3 or blob storage for invoice PDFs
- integrate OCR and layout extraction for invoice documents
- add role-based access control and SSO
- support GL coding and ERP sync
- add exception queues and SLA alerts
- build reconciliation workflows against bank or AP systems
- track approval bottlenecks by department

## Notes on realism

This repo intentionally avoids fake “magic AI” claims. It focuses on process reliability, auditability, and operational correctness. The implementation is simple enough to run locally and detailed enough to present as a serious engineering project.

## License

MIT
