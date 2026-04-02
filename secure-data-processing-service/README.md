# Secure Data Processing Service

A security-first data processing service built around encryption, least-privilege access, immutable audit trails, and compliance evidence generation.

This repository is a runnable local implementation of the README-backed project summary for **Secure Data Processing Service**. The original portfolio entry describes a platform that processes **500K+ sensitive records** and emphasizes encryption at rest, OAuth 2.0 and JWT-based authentication, MFA support, row and column permissions, secrets handling, input validation, immutable auditing, and auditor-ready reporting.

## What this repository includes

- FastAPI API with token issuance and MFA checks
- File-backed local KMS provider that behaves like a customer-managed key service for local development
- File-backed local secrets manager that mirrors the shape of AWS Secrets Manager integration
- Envelope-style encryption for stored payloads
- Row-level and column-level access control
- Append-only audit logging with hash chaining for tamper detection
- Compliance summary generation from audit evidence
- Docker, Kubernetes, and Terraform scaffolding
- Optional C++ utility for PII masking benchmarks and batch preprocessing
- Automated tests and smoke scripts

## Real-world framing

Most secure data systems fail at the seams rather than at the obvious spots. The API may authenticate correctly, but secrets live in env files forever. Payloads may be encrypted, but the service still logs sensitive fields. Audit trails may exist, but they are mutable and hard to prove to an external reviewer.

This project is intentionally centered on those seams. The goal is not to build a giant platform. The goal is to build a service that shows the control plane around sensitive processing: who can access data, what they can see, how records are encrypted, how keys rotate, and what evidence an auditor can pull without reverse engineering raw logs.

## Repository layout

```text
secure-data-processing-service/
├── app/
│   ├── api/
│   ├── security/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── cpp/
├── docs/
├── k8s/
├── scripts/
├── terraform/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Architecture

### 1. Identity and authentication

The service exposes `/auth/token` for password-plus-MFA login and returns a signed JWT with role and org claims. For local development, `/auth/mfa-demo/{username}` returns a TOTP code so the flow is easy to exercise without a phone authenticator.

Roles included in the seeded environment:

- `admin`: full access, can rotate keys and review audit evidence
- `processor`: can create records for its organization and read back full records in that org
- `analyst`: read-only within its organization and only sees policy-approved columns
- `auditor`: cross-org audit visibility and compliance-report access

### 2. Authorization and least privilege

The policy layer enforces:

- **row-level access** by organization
- **column-level access** by role

A processor in `north` can create records for `north`. An analyst in `north` can read those records, but personally identifying columns such as `name` and `email` are redacted. This mirrors the README’s requirement for fine-grained permissions at both row and column levels.

### 3. Encryption and key lifecycle

For local runs, encryption is handled by `LocalKMS`, which models customer-managed keys with rotation. Each payload is encrypted before storage and tagged with the active key id. When keys rotate, the service decrypts and re-encrypts records under the new active key and records the operation in the audit trail.

This keeps the API surface close to a KMS-backed deployment without making local setup depend on live AWS services.

### 4. Secrets handling

The repository includes a small `LocalSecretsManager` provider so the service retrieves secrets through a provider abstraction rather than directly from hard-coded config. In production, the same abstraction would map to AWS Secrets Manager.

### 5. Immutable auditing and compliance reporting

Every high-value action emits an audit event containing:

- timestamp
- actor
- action
- resource
- status
- structured metadata
- previous entry hash
- current entry hash

Because each entry includes the previous hash, the chain can be verified with `/audit/verify`. Compliance summaries aggregate those events into a reviewer-friendly report through `/audit/compliance-report`.

## Data model

### users

Stores identity, role, org, MFA secret, and active status.

### records

Stores encrypted payloads plus policy-relevant metadata such as org, classification, region, and department.

### audit_events

Stores the append-only audit history and hash chain.

### key_rotations

Tracks CMK rotations and the number of records re-encrypted.

## API summary

### Auth

- `POST /auth/token`
- `GET /auth/mfa-demo/{username}`

### Records

- `POST /records`
- `GET /records/{record_id}`
- `POST /records/rotate-keys`

### Audit and compliance

- `GET /audit/events`
- `GET /audit/verify`
- `GET /audit/compliance-report`

### Operations

- `GET /health`
- `GET /ready`

## Local setup

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed environment defaults

```bash
cp .env.example .env
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

The first boot creates:

- local SQLite database
- local KMS key file
- local secrets file
- seeded users
- audit log sink

## Seeded demo accounts

| Username | Password | Role | Org |
|---|---|---|---|
| `admin` | `ChangeMe123!` | admin | root |
| `processor_north` | `Processor123!` | processor | north |
| `analyst_north` | `Analyst123!` | analyst | north |
| `auditor_global` | `Auditor123!` | auditor | root |

## Example flow

### Get an MFA code for the local admin

```bash
curl http://127.0.0.1:8000/auth/mfa-demo/admin
```

### Exchange credentials for a token

```bash
curl -X POST http://127.0.0.1:8000/auth/token   -H "Content-Type: application/json"   -d '{"username":"admin","password":"ChangeMe123!","mfa_code":"123456"}'
```

### Create a restricted record

```bash
curl -X POST http://127.0.0.1:8000/records   -H "Authorization: Bearer <token>"   -H "Content-Type: application/json"   -d '{
    "subject_id": "CASE-9001",
    "org_id": "north",
    "classification": "restricted",
    "region": "midwest",
    "department": "claims",
    "payload": {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "record_type": "claim",
      "status": "pending",
      "priority": "high",
      "notes": "manual review"
    }
  }'
```

### Verify audit chain integrity

```bash
curl http://127.0.0.1:8000/audit/verify -H "Authorization: Bearer <token>"
```

## Scripts

### Seed sample records

```bash
python scripts/seed_demo.py
```

### Generate compliance summary artifact

```bash
python scripts/generate_compliance_report.py
```

### Run ingest benchmark

```bash
python scripts/benchmark_ingest.py --records 5000
```

### Run smoke test against a live local server

```bash
bash scripts/smoke_test.sh
```

## Tests

```bash
pytest
```

The tests cover:

- login and MFA exchange
- create and read flows
- row and column policy enforcement
- audit chain verification
- key rotation and re-encryption

## C++ utility

The portfolio summary lists both Python and C++ in the stack. To keep that believable without forcing a native dependency on every request path, the repository includes a small optional C++ utility under `cpp/` that performs PII masking on batch text input. It is useful for preprocessing or benchmarking paths where Python regex throughput becomes a bottleneck.

Build it with:

```bash
make cpp
```

## Docker

```bash
docker compose up --build
```

## Kubernetes

The `k8s/` folder includes:

- namespace
- deployment
- service
- network policy

These manifests are intentionally lightweight, but they capture the production deployment direction implied by the README: containerized service deployment with health checks and clear network boundaries.

## Terraform

The `terraform/` directory includes starter resources for:

- AWS KMS key
- AWS Secrets Manager secret

This keeps the infrastructure story aligned with the original project summary while staying small enough to understand in one pass.

## Observability and evidence design

This project does not pretend that application logs alone are enough for compliance. Instead it distinguishes between:

- operational health endpoints
- audit evidence
- compliance summaries

The audit chain is the source of truth for sensitive data access review.

## Design decisions and tradeoffs

### Why a local KMS abstraction instead of direct Fernet calls everywhere?

Because the security requirement is not just encryption. It is key ownership, rotation, and the ability to swap local providers for managed services later.

### Why SQLite locally?

Because it makes the project runnable in one command. The code paths are still shaped around policy checks, encrypted payload storage, and audit evidence, which are the parts that matter for the design discussion.

### Why keep MFA support built in?

Because the README explicitly calls out OAuth 2.0, JWT, and MFA support. Leaving MFA out would make the repository feel incomplete relative to the source spec.

### Why is the C++ piece optional?

Because the service core should stay easy to run locally, but the repository still needs a credible native path for security-sensitive preprocessing and performance-oriented workloads.

## License

MIT
