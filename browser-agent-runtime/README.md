# Browser Agent Runtime

A browser-native agent system for authenticated workflows, task execution, replayable traces, and safe browser actions.

This project is built around one core idea: browser automation is easy to demo and hard to run reliably. A production-grade browser agent needs task state, permissions, replay, observability, retry logic, and clean separation between planning and execution. This repository implements that runtime.

The stack is intentionally practical:

- **FastAPI** for control plane APIs
- **SQLAlchemy + PostgreSQL** for durable task and run state
- **Redis** for queueing, short-lived coordination, and worker signaling
- **Playwright** for browser execution
- **Docker Compose** for local orchestration
- **Structured step tracing** for replay, screenshots, and debugging

## Why this project exists

A simple script can log into a site and click buttons. That is not the hard part.

The hard part is answering questions like:

- What exactly happened during the run?
- Which action failed and why?
- Can the run be replayed safely?
- Which actions are allowed without confirmation?
- How do you keep session state isolated?
- How do you inspect the DOM and screenshots after a failure?
- How do you separate model suggestions from actual browser execution?

This runtime is designed to solve those problems.

## What it supports

The current implementation includes:

- persisted tasks and task runs
- background worker execution
- step-by-step action traces
- browser session reuse hooks
- screenshots for each step
- dry-run mode for safe local testing
- permission checks for dangerous actions
- validation between planned actions and executable tools
- replay of previous runs
- API endpoints for inspection and status polling

## Architecture

```text
Client
  |
  v
FastAPI Control Plane
  - create task
  - inspect task runs
  - replay failures
  - fetch artifacts
  |
  +--> PostgreSQL
  |      - tasks
  |      - task runs
  |      - action logs
  |      - artifacts
  |
  +--> Redis
  |      - worker queue
  |      - lightweight locks / status
  |
  v
Worker
  - picks queued runs
  - plans actions
  - executes browser tools
  - records traces
  - captures screenshots
  - updates run state
  |
  v
Playwright Browser Runtime
```

## Execution model

The system is organized around a simple hierarchy:

- **Task**: the user request, such as _“log into a billing portal and download the latest invoice”_
- **Task Run**: one concrete attempt to execute a task
- **Action Log**: each step taken during the run, including input, output, timing, and status
- **Artifact**: evidence captured during execution, such as screenshots, DOM snapshots, or downloads

That structure makes it possible to retry, audit, and replay runs without losing context.

## Project layout

```text
browser-agent-runtime/
├── app/
│   ├── api/
│   │   ├── health.py
│   │   ├── runs.py
│   │   └── tasks.py
│   ├── runtime/
│   │   ├── browser_tools.py
│   │   ├── executor.py
│   │   ├── permissions.py
│   │   └── planner.py
│   ├── services/
│   │   ├── queue.py
│   │   └── tasks.py
│   ├── utils/
│   │   └── logging.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── worker.py
├── scripts/
│   └── demo_seed.py
├── tests/
│   ├── test_permissions.py
│   └── test_planner.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## Core concepts

### 1. Planning is separate from execution

The planner returns a list of proposed actions. The executor validates that each action is allowed, that the action schema is correct, and that the tool exists before anything is sent to the browser runtime.

This is the most important design decision in the repository. The planner can be swapped later for a model-backed policy, but browser execution remains deterministic and controlled by your runtime.

### 2. Safety is built into action classes

Every action belongs to a permission class:

- `read_only`
- `navigation`
- `form_fill`
- `submission`

Runs can be created in `dry_run` mode to test trajectories without actually submitting forms.

### 3. Every run leaves evidence

Each executed action records:

- start and end timestamps
- parameters
- result payload
- failure reason
- screenshot path
- DOM summary when available

That makes it much easier to debug selector drift, auth issues, or wrong assumptions.

## Supported actions

The default tool set includes:

- `navigate`
- `click`
- `type`
- `fill_form`
- `extract_text`
- `wait_for`
- `screenshot`
- `submit`

You can extend this by registering new browser tools and mapping them into the executor.

## Quick start

### Option A: run locally with Python

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -e .
playwright install chromium
```

3. Start infrastructure

```bash
docker compose up -d postgres redis
```

4. Copy environment variables

```bash
cp .env.example .env
```

5. Start the API

```bash
uvicorn app.main:app --reload
```

6. Start the worker in a second terminal

```bash
python -m app.worker
```

### Option B: run everything with Docker Compose

```bash
docker compose up --build
```

The API will be available on `http://localhost:8000`.

## Environment variables

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/browser_agent
REDIS_URL=redis://redis:6379/0
ARTIFACT_DIR=./artifacts
DEFAULT_HEADLESS=true
DEFAULT_DRY_RUN=true
WORKER_POLL_INTERVAL=2
```

## Example API flow

### Create a task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice portal demo",
    "description": "Log into the portal and download the latest invoice",
    "instruction": "Open the billing page, inspect recent invoices, and capture proof.",
    "start_url": "https://example.com/login",
    "dry_run": true
  }'
```

### Enqueue a run

```bash
curl -X POST http://localhost:8000/tasks/<task_id>/runs
```

### Inspect all runs for the task

```bash
curl http://localhost:8000/tasks/<task_id>/runs
```

### Inspect one run in detail

```bash
curl http://localhost:8000/runs/<run_id>
```

### Replay a run

```bash
curl -X POST http://localhost:8000/runs/<run_id>/replay
```

## Example plan format

The planner emits actions in a structured format like this:

```json
[
  {
    "name": "navigate",
    "permission": "navigation",
    "params": {
      "url": "https://example.com/login"
    }
  },
  {
    "name": "type",
    "permission": "form_fill",
    "params": {
      "selector": "#email",
      "text": "{{EMAIL}}"
    }
  },
  {
    "name": "type",
    "permission": "form_fill",
    "params": {
      "selector": "#password",
      "text": "{{PASSWORD}}"
    }
  },
  {
    "name": "click",
    "permission": "submission",
    "params": {
      "selector": "button[type=submit]"
    }
  }
]
```

In this starter version, the planner is rule-based and intentionally deterministic. It is easy to understand, easy to test, and a good base for adding model-backed planning later.

## Replay and debugging model

A common failure mode in browser agents is that you do not know whether the task failed because of:

- wrong selector
- unexpected page redirect
- stale login
- broken assumption in the plan
- timing issue
- permission rejection
- submission blocked in dry-run mode

To make that visible, every run stores a structured action timeline and artifact paths. In a real debugging workflow, you would inspect the run in this order:

1. run summary and final state
2. action log sequence
3. screenshot around the first failure
4. DOM summary or extracted text
5. replay the run with updated selectors or lower concurrency

## Persistence model

### Tables

- `tasks`
  - stable task definition
- `task_runs`
  - concrete execution attempts
- `action_logs`
  - step-level execution records
- `artifacts`
  - screenshots and other evidence

The database schema is intentionally compact. It is large enough to support replay, observability, and debugging, but small enough to understand quickly.

## Dry-run mode

The fastest way to test the runtime safely is to keep `dry_run=true`.

In dry-run mode:

- navigation still happens
- reads still happen
- screenshots still happen
- non-destructive clicks still happen
- `submit` actions are blocked unless explicitly allowed

This helps validate workflows without risking real side effects.

## Local development workflow

### Run tests

```bash
pytest
```

### Format code

```bash
ruff check .
ruff format .
```

### Seed demo data

```bash
python scripts/demo_seed.py
```

## Extending the runtime

### Add a new browser tool

1. implement the async method in `browser_tools.py`
2. add the action name to the executor dispatch table
3. define the permission class
4. add tests for both allowed and rejected behavior

### Replace the planner

The planner currently uses rule-based templates. To add a model-backed planner later:

1. keep the same `PlannedAction` schema
2. call your model outside the executor
3. validate the returned action list
4. only then pass actions into the runtime

That preserves the safety boundary.

## Design tradeoffs

### Why not let the model drive the browser directly?

Because it makes the runtime opaque, hard to debug, and much riskier. The planner should suggest actions. The runtime should remain the single authority that decides what is valid to execute.

### Why not use a giant workflow engine immediately?

This repository is intentionally small enough to understand in a day. It gives you the right primitives first. Once the runtime is trusted, you can layer on richer orchestration, multi-agent flows, or Kubernetes-managed browser pools.

### Why both Redis and Postgres?

Postgres is the source of truth for durable state. Redis is useful for queue signaling, lightweight coordination, and fast worker polling. Treating them differently keeps the architecture clean.

## Known limitations

This is a serious starter implementation, but it is still a starter implementation.

Current limitations:

- the planner is rule-based rather than model-backed
- session persistence is scaffolded but not yet fully isolated per user account
- downloaded files are not yet streamed back through the API
- DOM snapshots are summarized rather than fully versioned
- multi-tab support is not implemented
- browser pool scaling is not implemented

## Roadmap

- cookie jar persistence per browser session
- encrypted credentials vault integration
- full run replay from stored action logs
- browser pool manager
- remote browser workers
- WebSocket streaming of live traces
- richer selector strategies with fallback heuristics
- configurable approval workflows for dangerous actions
- OpenTelemetry integration for distributed traces


## License

MIT
