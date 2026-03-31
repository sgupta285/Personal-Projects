# Human Data Collection Platform

Human Data Collection Platform is a GitHub-ready full-stack project for collecting rankings, preference data, classifications, critiques, and moderation decisions with built-in quality control. It is designed around realistic human-in-the-loop operations instead of a generic form builder.

The core idea is simple: if you want useful human feedback, you need more than a table of prompts and answers. You need task assignment, role-aware workflows, seed tasks, reviewer adjudication, anomaly detection, quality metrics, export paths, and an interface that operators can move through quickly.

## Why this project matters

A lot of labeling tooling looks complete on the surface but breaks down operationally:

- operators get unbalanced or repetitive queues
- reviewers cannot easily inspect low-quality work
- admins have no fast way to audit throughput or agreement
- seed tasks exist in theory but are not tied back to metrics
- the resulting data has weak provenance and is hard to trust

This repository is built to show the opposite. It treats annotation as an operational system with feedback loops.

## Core use cases

The starter platform supports five task families directly from the project brief:

- **ranking**
- **label classification**
- **pairwise preference**
- **freeform critique**
- **moderation review**

The included demo batch covers all five so the platform can be seeded immediately.

## What is included

### Backend API
- FastAPI service with routes for users, bulk task ingest, next-task assignment, response submission, pending review queues, and admin metrics
- SQLite-backed local persistence using the Python standard library for easy startup
- schema-driven request and response validation with Pydantic
- repository layer with clear extension points for PostgreSQL and Redis-backed workers

### Quality-control features
- seed task scoring when a gold answer is available
- anomaly detection for empty, repetitive, or implausibly fast responses
- reviewer adjudication with approval, rejection, or rework decisions
- agreement summaries for classification-style work
- admin metrics for queue state, throughput, review volume, and seed-task accuracy

### Frontend starter
- lightweight React + TypeScript dashboard scaffold
- operator-friendly layout that can be extended into dedicated annotator, reviewer, and admin surfaces
- clean styling so the repo presents well on GitHub screenshots and demos

### Operations tooling
- sample task dataset in JSON
- seed script for demo setup
- Docker and docker-compose for local bootstrapping
- unit and API tests

## Project structure

```text
human-data-collection-platform/
├── app/
│   ├── api/
│   ├── services/
│   │   ├── assignment_engine.py
│   │   ├── quality.py
│   │   └── repository.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── schemas.py
├── data/
│   └── sample_tasks.json
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── styles.css
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   └── seed_demo.py
├── tests/
│   ├── test_api.py
│   ├── test_assignment_engine.py
│   └── test_quality.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Architecture

The platform is built around six practical layers.

### 1. Task layer
Each task stores:
- task type
- payload JSON
- optional gold answer
- priority
- batch name
- requires-review flag
- seed-task flag

That keeps the system generic enough to support multiple labeling modes without rewriting the core workflow.

### 2. Assignment layer
The assignment engine chooses the next task based on:
- the operator's role
- whether the user has already seen the task
- task priority
- seed-task preference
- queue status

The starter engine is deterministic and simple on purpose. It is easy to test, easy to explain, and easy to upgrade later with balancing logic, skill routing, or active-learning policies.

### 3. Response layer
When an annotator submits work, the system stores:
- the assignment link
- the task reference
- the user reference
- the raw response JSON
- time spent
- computed quality flags

That means the data record carries both the answer and the operational context around how the answer was produced.

### 4. Review layer
Tasks can be routed into a reviewer queue. Reviewers can:
- approve
- reject
- mark for rework

This gives the repo a real second-pass workflow instead of stopping at first-touch annotation.

### 5. Quality-control layer
The quality module currently computes:
- seed task score
- anomaly flags
- simple agreement summary for classification outputs

These are intentionally implemented as transparent rules rather than opaque heuristics. They are easy to trust and easy to extend.

### 6. Admin analytics layer
The admin metrics endpoint exposes:
- open tasks
- in-progress tasks
- pending-review tasks
- completed tasks
- total responses
- total reviews
- seed-task accuracy
- average review score
- throughput by task type
- agreement summary

That makes the repo useful not only as a collector of labels, but as a lightweight operations cockpit.

## Example workflow

A realistic team loop looks like this:

1. Create users for annotators, reviewers, and admins.
2. Bulk import tasks from a batch.
3. Assign the next task to an annotator.
4. Submit an answer with time spent.
5. Route the task into pending review.
6. Let a reviewer approve or reject it.
7. Inspect admin metrics and quality summaries.
8. Export or reuse the stored responses downstream.

## Local setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd human-data-collection-platform
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

The default configuration uses a local SQLite database so the project is easy to boot without any external dependencies.

### 3. Seed demo data

```bash
python scripts/seed_demo.py
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

## Docker setup

```bash
cp .env.example .env
docker compose up --build
```

This starts:
- the FastAPI backend on port 8000
- Redis on port 6379
- the Vite frontend on port 5173

The backend does not require Redis for the starter flow, but it is included because production annotation systems usually need queue fanout, locks, or background checks.

## Example API usage

Create a user:

```bash
curl -X POST http://localhost:8000/api/users   -H "Content-Type: application/json"   -d '{
    "name": "Alicia Annotator",
    "role": "annotator",
    "email": "annotator@example.com",
    "skill_level": "general"
  }'
```

Bulk load tasks:

```bash
curl -X POST http://localhost:8000/api/tasks/bulk   -H "Content-Type: application/json"   -d @data/sample_tasks.json
```

Note: the API expects a wrapper object of the shape:

```json
{
  "tasks": [
    {
      "task_type": "classification",
      "priority": 95,
      "requires_review": true,
      "seed_task": true,
      "payload": {"instruction": "..."},
      "gold": {"key": "label", "label": "product_defect"}
    }
  ]
}
```

Get the next task for an annotator:

```bash
curl -X POST http://localhost:8000/api/assignments/next/1
```

Submit a response:

```bash
curl -X POST http://localhost:8000/api/responses   -H "Content-Type: application/json"   -d '{
    "assignment_id": 1,
    "response": {"label": "product_defect"},
    "time_spent_seconds": 14
  }'
```

Get admin metrics:

```bash
curl http://localhost:8000/api/admin/metrics
```

## How to extend this into a stronger production system

This starter repo is deliberately practical, but it also leaves obvious upgrade paths:

### Data and infrastructure
- move persistence from SQLite to PostgreSQL
- add Redis queues for assignment fanout, worker jobs, and throttling
- store exports and batch artifacts in S3 or another blob store

### Workflow quality
- add inter-rater agreement by task and cohort
- sample audit queues dynamically based on operator history
- add reviewer calibration tasks and blind rechecks
- support consensus workflows for difficult tasks

### UX and speed
- build dedicated task UIs per task type instead of a shared dashboard shell
- add hotkeys, skip reasons, keyboard-only review, and queue filters
- stream queue updates with WebSockets

### Security and auth
- add RBAC with Auth0 or a custom session model
- log admin actions and reviewer overrides
- separate research-only and production projects cleanly

## Testing

Run the test suite with:

```bash
pytest
```

The included tests cover:
- assignment selection behavior
- quality-control scoring
- API flow from user creation to review and admin metrics

