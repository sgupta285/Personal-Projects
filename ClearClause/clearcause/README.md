# ClearCause MVP

> AI-powered contract analysis that makes legal documents readable and actionable.

Upload a lease, Terms of Service, or SaaS agreement. Get plain-language summaries, risk scores, and negotiation prompts — no law degree required.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (React + Tailwind)                              │
│  S3 + CloudFront (CDN, HTTPS)                            │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│  API Gateway (HTTP API)  +  Cognito JWT Auth              │
└──────┬───────────────────────────────┬───────────────────┘
       │                               │
┌──────▼──────┐              ┌─────────▼──────────┐
│  Upload λ   │──── SQS ────▶│  Analyze λ          │
│  (30s, 256MB)│              │  (300s, 1024MB)     │
└──────┬──────┘              │                     │
       │                     │  1. Extract (Textract)│
       ▼                     │  2. Chunk (semantic)  │
   ┌────────┐                │  3. Detect (regex+ML) │
   │  S3    │                │  4. Summarize (GPT-4) │
   │ (docs) │                │  5. Score (hybrid)    │
   └────────┘                │  6. Report            │
                             └─────────┬────────────┘
                                       │
                             ┌─────────▼───────────┐
                             │  Report λ (PDF gen)  │
                             └─────────────────────┘

Storage: DynamoDB (jobs, results) + S3 (documents, reports)
Auth:    Cognito (email + password)
AI/ML:   OpenAI GPT-4o-mini + regex clause detection
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Tailwind CSS, Vite | SPA with file upload, analysis dashboard |
| API | API Gateway (HTTP) | REST endpoints with JWT auth |
| Auth | Cognito | User registration, login, JWT tokens |
| Compute | Lambda (Python 3.11) | Serverless functions for upload, analyze, report |
| Queue | SQS | Async document processing pipeline |
| Database | DynamoDB | Jobs tracking, analysis results |
| Storage | S3 | Document storage (KMS encrypted) |
| AI | OpenAI GPT-4o-mini | Clause summarization, executive summaries |
| OCR | AWS Textract | PDF text extraction |
| CDN | CloudFront | Frontend delivery, HTTPS |
| IaC | Terraform | Infrastructure automation |

## Project Structure

```
clearcause-mvp/
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main application (all components)
│   │   ├── components/          # (extracted components for scale)
│   │   ├── utils/               # API client, auth helpers
│   │   └── styles/              # Tailwind config
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── lambdas/
│   │   ├── upload/handler.py    # File upload + S3 storage
│   │   ├── analyze/handler.py   # Core AI analysis pipeline
│   │   └── report/handler.py    # PDF report generation
│   ├── shared/                  # Shared utilities
│   └── requirements.txt
├── infrastructure/
│   └── terraform/
│       └── main.tf              # Complete AWS infrastructure
├── deploy.sh                    # One-command deployment
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- AWS CLI configured with appropriate credentials
- Terraform 1.5+
- OpenAI API key

### 1. Clone and Install

```bash
git clone <repo-url> && cd clearcause-mvp

# Frontend
cd frontend && npm install && cd ..

# Backend
cd backend && pip install -r requirements.txt && cd ..
```

### 2. Configure

Create `infrastructure/terraform/terraform.tfvars`:

```hcl
environment    = "dev"
openai_api_key = "sk-..."
aws_region     = "us-east-1"
```

### 3. Deploy

```bash
chmod +x deploy.sh
./deploy.sh dev
```

This will:
1. Package all Lambda functions with dependencies
2. Deploy AWS infrastructure via Terraform
3. Build and deploy the React frontend to S3/CloudFront

### 4. Local Development

```bash
# Frontend (hot reload)
cd frontend && npm run dev

# Backend (local testing with SAM)
sam local start-api
```

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/upload` | Upload a document for analysis | JWT |
| `GET` | `/api/jobs/{id}` | Check analysis status | JWT |
| `GET` | `/api/results/{id}` | Get analysis results | JWT |
| `GET` | `/api/report?job_id=X` | Generate PDF report | JWT |

### Upload Example

```bash
curl -X POST $API_URL/api/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "lease.pdf",
    "contentType": "application/pdf",
    "file": "<base64-encoded-pdf>"
  }'
```

Response:
```json
{
  "job_id": "a1b2c3d4-...",
  "status": "uploaded",
  "message": "Document uploaded. Analysis in progress."
}
```

## Analysis Pipeline

The core analysis runs in 6 steps:

1. **Extract** — AWS Textract (OCR) or PyMuPDF extracts text from uploaded PDFs
2. **Chunk** — Text is split into ~500-token semantic chunks with 50-token overlap
3. **Detect** — Regex + keyword patterns identify 12 clause types (arbitration, auto-renewal, liability caps, etc.)
4. **Summarize** — GPT-4o-mini generates 8th-grade reading level summaries for each clause
5. **Score** — Hybrid risk scoring: clause presence × severity weights, contextualized by LLM
6. **Report** — Results stored in DynamoDB; PDF export available via ReportLab

### Clause Types Detected

| Clause | Risk Weight | Category |
|--------|------------|----------|
| Binding Arbitration | High (3) | Dispute Resolution |
| Unilateral Modification | High (3) | Terms |
| Liability Limitation | High (3) | Liability |
| Non-Compete | High (3) | Restrictions |
| Auto-Renewal | Medium (2) | Terms |
| Data Sharing | Medium (2) | Privacy |
| Indemnification | Medium (2) | Liability |
| Termination Without Cause | Medium (2) | Terms |
| Data Retention | Medium (2) | Privacy |
| IP & Content Rights | Low (1) | IP |
| Governing Law | Low (1) | Dispute Resolution |
| Force Majeure | Low (1) | Liability |

## Cost Estimates (Monthly)

| Resource | Cost |
|----------|------|
| Lambda compute | ~$50 |
| RDS/DynamoDB | ~$30 |
| OpenAI API (GPT-4o-mini) | ~$150 |
| S3 + CloudFront | ~$50 |
| Textract OCR | ~$20 |
| **Total** | **~$300/mo** |
| **Cost per document** | **~$0.25** |

## Security

- All documents encrypted at rest (S3 KMS)
- TLS 1.3 in transit (CloudFront)
- Cognito JWT authentication on all API endpoints
- IAM least-privilege Lambda roles
- S3 bucket policies block public access
- Document TTL: 30-day auto-expiry

## Evaluation Metrics (Week 5-6)

| Metric | Target | How Measured |
|--------|--------|-------------|
| Citation accuracy | ≥95% | % summaries with valid source links |
| Clause detection recall | ≥85% | % known clause types found in test set |
| Risk scoring consistency | κ ≥ 0.7 | Inter-rater reliability vs. legal experts |
| Summarization readability | Grade ≤ 8 | Flesch-Kincaid grade level |
| Processing time | < 30s | P95 latency for 10-page PDFs |

---

**Disclaimer:** ClearCause is for informational purposes only and does not constitute legal advice. Consult a qualified attorney for your specific situation.
