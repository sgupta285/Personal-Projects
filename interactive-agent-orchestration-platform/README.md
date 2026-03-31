# Interactive Agent Orchestration Platform

An operator-facing control plane for long-running, multi-step agent workflows.

This repository is built around a simple idea: autonomy is only useful when people can understand what the system is doing, step in when it drifts, and replay failures without guessing. The project focuses on that layer between raw agent execution and user trust.

Instead of treating an agent like a single black-box function call, this platform models each run as a sequence of named steps with explicit tool choices, rationale, cost, latency, intermediate state, and operator interventions. The result is a system that is easier to observe, pause, retry, and improve over time.

## What the project does

The platform acts as the control surface for multi-step AI agents.

It supports:

- creating and tracking agent runs
- recording step-by-step execution traces
- streaming live state changes to an operator console
- exposing operator controls such as pause, resume, retry from step, prompt swap, and model switch
- capturing cost, latency, and intervention metrics
- separating orchestration logic from transport layers so the runtime can be reused by the API, worker, and realtime services

The repo is designed to show the architecture and workflow of a production-oriented orchestration layer, not just a toy demo that returns a final answer.

## Why this project is useful

Most agent demos stop at task completion. Real systems need more than that.

Operators usually want to know:

- what tool the agent picked and why
- which step is running right now
- where the run failed
- how expensive the run was
- whether the model recovered on its own or needed human help
- how to retry from the exact failure point instead of re-running everything

This project makes those questions first-class concepts in the runtime.

## Repository layout

```text
interactive-agent-orchestration-platform/
├── apps/
│   ├── api/         # REST API for run creation, inspection, and interventions
│   ├── realtime/    # WebSocket service for streaming run events to the UI
│   ├── worker/      # Queue consumer that executes runs asynchronously
│   └── web/         # React operator console
├── packages/
│   └── core/        # Shared orchestration engine, planner, metrics, and tests
├── data/            # Sample payloads and generated smoke-test output
├── docs/            # Architecture notes
├── scripts/         # Validation and demo scripts
└── docker-compose.yml
```

## Core concepts

### 1. Run
A run is a single execution of an agent against a user request.

Each run stores:

- agent name
- user intent
- model and prompt config
- current run status
- cumulative cost and latency
- the current step index
- failure reason when applicable
- tags for filtering or reporting
- the complete history of operator interventions

### 2. Step trace
Each run contains a list of step traces.

A step trace captures:

- step name
- chosen tool
- rationale for that tool choice
- structured input
- structured output
- status
- retry count
- step latency
- step cost
- start and completion timestamps

This is the most important unit for debugging and replay.

### 3. Event stream
The runtime emits events whenever something important happens.

Examples:

- `run.created`
- `run.started`
- `step.started`
- `step.completed`
- `step.failed`
- `run.cost_updated`
- `operator.intervened`
- `run.completed`

These events are what the realtime service forwards to the frontend.

### 4. Operator intervention
The platform treats human intervention as part of the runtime, not an afterthought.

Supported intervention types in the current scaffold:

- pause
- resume
- retry from step
- swap prompt config
- switch model
- override output

## How the project is structured technically

### Shared core package
The orchestration engine lives in `packages/core`.

This package contains:

- typed run and event schemas
- a lightweight planner that turns user intent into step drafts
- the in-memory run store used for local development and smoke testing
- the execution engine that updates run state over time
- metrics helpers for cost, latency, failure rate, and intervention rate
- tests for execution, failure handling, and retry behavior

This is the most complete and most validated part of the repository.

### API service
The API service is a TypeScript Express application that exposes endpoints to:

- create a run
- list runs
- inspect a run and its event history
- trigger execution
- record operator interventions

The API imports the shared core package rather than duplicating runtime logic.

### Realtime service
The realtime service is a small WebSocket server that forwards run events to connected clients. It subscribes to the shared engine and pushes structured updates to the frontend.

In a fuller deployment, this service would typically sit behind Redis pub/sub or a broker-backed fanout layer so that events from many workers can be pushed to many clients.

### Worker service
The worker listens to a Redis-backed queue and executes runs asynchronously. The current scaffold shows the intended boundary clearly:

- API receives run requests
- worker consumes queued run IDs
- core engine performs execution
- realtime service streams the resulting events

### Web console
The frontend is a React + TypeScript operator console scaffold that shows:

- top-line metrics
- a recent runs table
- per-run execution details
- step cards with tool usage and rationale
- intervention history

The UI currently uses mock data so the repo stays inspectable without requiring the full backend stack to be running.

## Example workflow

A typical run looks like this:

1. An operator or upstream service creates a run with a user intent.
2. The planner expands that intent into a sequence of named steps.
3. The API stores the run in queued state.
4. A worker picks up the run and begins execution.
5. The engine emits structured events as steps start and complete.
6. The realtime service forwards those events to the UI.
7. If a step fails, the operator can inspect the trace and retry from that point.
8. Metrics capture total latency, total cost, and whether intervention was needed.

## Running the validated core package locally

The core orchestration package is the part I validated directly in this environment.

From the repo root:

```bash
npm run build:core
npm run test:core
npm run smoke:core
```

What those commands do:

- `build:core` compiles the shared TypeScript package with `tsc`
- `test:core` runs the Node test suite against the compiled output
- `smoke:core` creates a sample run, executes it, calculates summary metrics, and writes a sample JSON artifact to `data/sample-run-output.json`

## Running the full stack locally

### Prerequisites

- Node.js 22+
- npm 10+
- Docker and Docker Compose
- Redis if you want to run the worker without Docker

### Option 1: run the full stack with Docker

```bash
docker compose up --build
```

This starts:

- Redis on `6379`
- API on `8080`
- realtime service on `8090`
- React UI on `5173`
- worker process connected to Redis

### Option 2: run services manually

Install workspace dependencies first:

```bash
npm install
npm --workspace apps/api install
npm --workspace apps/realtime install
npm --workspace apps/worker install
npm --workspace apps/web install
```

Then start each service in a separate terminal:

```bash
npm run build:core
npm --workspace apps/api run dev
npm --workspace apps/realtime run dev
npm --workspace apps/worker run dev
npm --workspace apps/web run dev
```

## API reference

### Health check

```http
GET /health
```

### Create a run

```http
POST /runs
Content-Type: application/json
```

Example body:

```json
{
  "agentName": "billing-agent",
  "userIntent": "Log into the billing portal, download the latest invoice, and email the result to finance.",
  "model": "gpt-4.1-mini",
  "promptConfig": "default.operator.v1",
  "tags": ["billing", "finance"]
}
```

### List runs and summary metrics

```http
GET /runs
```

### Inspect a run

```http
GET /runs/:runId
```

### Trigger execution

```http
POST /runs/:runId/execute
Content-Type: application/json
```

Example body:

```json
{
  "failAtStepIndex": 1
}
```

That option is especially useful when testing operator controls and failure handling.

### Record an intervention

```http
POST /runs/:runId/interventions
Content-Type: application/json
```

Example body:

```json
{
  "actor": "operator@local",
  "type": "retry_from_step",
  "note": "Retry after updating selector",
  "details": {
    "stepIndex": 1
  }
}
```

## Current design choices

### Why the demo store is in-memory
For a project repository like this, in-memory state keeps the orchestration engine easy to inspect and test. It also keeps the shared package independent from any single persistence backend.

In a production version, that store would be replaced by:

- PostgreSQL for canonical run and step state
- Redis for queue coordination, locks, and fanout
- object storage for larger artifacts like screenshots or DOM snapshots

### Why the frontend currently uses mock data
The UI is included to demonstrate the operator workflow and repo completeness without forcing a dependency-heavy build in every environment. The components are wired so that replacing mock data with live API and WebSocket data is straightforward.

### Why the execution engine is deterministic enough for testing
Agent systems are hard to evaluate when every run is fully stochastic. The execution scaffold here keeps timing and cost accumulation predictable enough for regression tests, while still showing the shape of a real orchestration flow.

## What is already validated

I validated the shared orchestration package directly:

- TypeScript compilation succeeds for `packages/core`
- the core test suite passes
- the smoke script runs successfully and writes sample output

That means the run model, step tracking, retry behavior, and metrics layer are working as checked code paths.

## What is scaffolded but not dependency-tested in this environment

The following parts are included as real project structure and code, but were not installed and executed end to end in this container because third-party packages for Express, ws, React, Vite, and Redis clients are not preinstalled here:

- API service
- realtime WebSocket service
- worker service
- frontend build
- Docker-based runtime

The repository includes everything needed to run those normally in a regular local environment.

## License

MIT
