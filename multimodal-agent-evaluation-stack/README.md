# Multimodal Agent Evaluation Stack

A production-style evaluation platform for measuring how well AI agents perform across tasks that include text, tools, screenshots, browser state, action histories, and structured outputs.

This repository is not a single benchmark script. It is a complete evaluation stack built around five concerns that matter in real agent systems:

1. **Benchmark design**: define tasks with clear expected behavior and frozen versions
2. **Run capture**: store complete trajectories, tool calls, screenshots, latency, cost, outputs, and evaluator judgments
3. **Evaluation**: support exact checks for deterministic tasks and rubric-based grading for open-ended tasks
4. **Failure analysis**: classify bad planning, wrong tool usage, invalid state assumptions, timeouts, and hallucinated completion
5. **Comparison and reproducibility**: compare prompts, models, tool interfaces, and benchmark versions over time

The project is intentionally structured so it can grow from a single-machine dev workflow into a team-facing evaluation platform with experiment tracking and dashboards.

---

## What this project does

The stack helps answer questions such as:

- Did the agent complete the task?
- How many steps did it take?
- Did it use the right tools?
- Was the recovery behavior reasonable after failure?
- How much latency and cost did the run incur?
- Was the output format valid?
- Which prompt, model, or tool-interface change actually improved quality?

The repository includes:

- a **FastAPI backend** for benchmark management, run ingestion, evaluation, analysis, and reporting
- a **React + TypeScript dashboard** for browsing runs, scorecards, and failure patterns
- a **benchmark registry** with versioned JSON task definitions
- a **trajectory evaluator** with exact-match and rubric-based scoring
- a **failure-mode analyzer** for common agent breakdowns
- an **MLflow integration hook** for logging runs and metrics into experiment tracking
- a **demo runner** for creating reproducible example runs without needing a live browser agent
- **Docker and docker-compose** for local orchestration

---

## Why this project is useful

A lot of agent demos look strong until you ask basic operational questions:

- what changed between model versions?
- where are the failures concentrated?
- are longer traces actually better or just more expensive?
- do successful runs recover from early mistakes?
- are tool-interface changes improving success rate or just shifting costs?

This stack makes those questions measurable.

It is especially useful when you are evaluating:

- browser agents
- tool-using copilots
- document processing agents
- structured extraction workflows
- support or operations agents with multi-step actions

---

## Architecture

### Backend

The backend is organized around the lifecycle of a benchmarked run:

1. **Benchmarks** define expected behavior, environment metadata, benchmark version, and evaluator configuration.
2. **Runs** capture a specific execution attempt with model configuration, input, trajectory, tool traces, screenshots, outputs, latency, and cost.
3. **Evaluations** score the run using deterministic or rubric-based evaluators.
4. **Analysis** classifies likely failure modes and computes summary metrics.
5. **Reports** aggregate run-level metrics for comparisons across models, prompts, datasets, and tool interfaces.

### Frontend

The dashboard is intentionally simple and practical. It focuses on the views an engineer or researcher actually wants:

- benchmark list
- run list with filterable metadata
- per-run trajectory view
- metrics summary cards
- failure-mode breakdown
- quick comparisons by model name, benchmark id, or prompt version

### Storage strategy

For local development, the backend defaults to SQLite so the project is easy to run immediately.

For team or production-like use, switch to PostgreSQL by setting `DATABASE_URL`.

### Experiment tracking

MLflow is integrated as an optional dependency. If `MLFLOW_TRACKING_URI` is configured, evaluation runs will also be logged to MLflow so you can version:

- prompt configs
- model names
- datasets / benchmark versions
- evaluator settings
- summary metrics

---

## Repository layout

```text
multimodal-agent-evaluation-stack/
├── backend/
│   ├── app/
│   │   ├── analysis.py
│   │   ├── benchmarks.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── evaluators.py
│   │   ├── main.py
│   │   ├── mlflow_client.py
│   │   ├── models.py
│   │   ├── runner.py
│   │   └── schemas.py
│   ├── scripts/
│   │   └── seed_demo.py
│   ├── tests/
│   │   ├── test_analysis.py
│   │   ├── test_evaluators.py
│   │   └── test_runner.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── benchmarks/
│   ├── browser_export_report_v1.json
│   ├── compare_pricing_plans_v1.json
│   └── summarize_multi_modal_case_v1.json
├── docs/
│   └── api_examples.md
├── docker-compose.yml
└── .gitignore
```

---

## Core evaluation concepts

### 1. Benchmark tasks

A benchmark task defines:

- `benchmark_id`
- `name`
- `version`
- `task_type`
- `instructions`
- `expected_tools`
- `expected_output`
- `evaluator_type`
- `metadata`

This lets you freeze benchmark versions so experiments stay comparable.

### 2. Trajectory data

Every run stores a step-by-step trajectory. Each step includes:

- timestamp or order index
- tool name
- action summary
- observation
- latency
- success flag
- optional screenshot reference
- optional browser or environment state reference

### 3. Evaluation modes

Two evaluation modes are included out of the box:

#### Exact match evaluator
Best for deterministic outputs:

- exact string match
- JSON subset checks
- required field coverage
- expected tool usage checks

#### Rubric evaluator
Best for open-ended tasks:

- output quality
- completeness
- tool selection quality
- trajectory efficiency
- recovery behavior
- format validity

### 4. Failure analysis

The analyzer classifies runs into common failure buckets:

- `bad_planning`
- `wrong_tool`
- `invalid_state_assumption`
- `timeout`
- `hallucinated_completion`
- `unknown`

This makes it much easier to understand why a benchmark is failing rather than simply seeing a low score.

---

## Local development

### Prerequisites

Backend:

- Python 3.11+

Frontend:

- Node.js 20+
- npm 10+

Optional services:

- PostgreSQL
- MLflow server

### 1. Clone and enter the repo

```bash
git clone <your-repo-url>
cd multimodal-agent-evaluation-stack
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

Interactive docs:

```text
http://localhost:8000/docs
```

### 3. Seed demo benchmarks and runs

In another terminal:

```bash
cd backend
python scripts/seed_demo.py
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will run at:

```text
http://localhost:5173
```

---

## Docker workflow

From the repository root:

```bash
docker compose up --build
```

This starts:

- backend API on port `8000`
- frontend dashboard on port `5173`
- PostgreSQL on port `5432`

If you want to keep using SQLite instead of PostgreSQL, the backend can still run directly outside Docker.

---

## Environment variables

### Backend

Create `backend/.env` if you want custom settings.

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Service name | `multimodal-agent-evaluation-stack` |
| `ENVIRONMENT` | dev / test / prod | `dev` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./agent_eval.db` |
| `API_HOST` | API bind host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `MLFLOW_TRACKING_URI` | Optional MLflow server URI | empty |
| `MLFLOW_EXPERIMENT_NAME` | MLflow experiment name | `agent-evals` |
| `DEFAULT_BENCHMARK_DIR` | Path to bundled benchmark JSON files | `../benchmarks` |

### Frontend

Create `frontend/.env` if needed.

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

---

## API overview

### Health check

```http
GET /health
```

### Benchmarks

```http
GET /benchmarks
POST /benchmarks/load-defaults
POST /benchmarks
GET /benchmarks/{benchmark_id}
```

### Runs

```http
GET /runs
POST /runs
GET /runs/{run_id}
POST /runs/{run_id}/evaluate
POST /runs/{run_id}/analyze
POST /runs/demo/{benchmark_id}
```

### Reports

```http
GET /reports/summary
GET /reports/failure-modes
```

Example request and response payloads are included in `docs/api_examples.md`.

---

## Example workflow

A normal experiment loop looks like this:

1. Load default benchmarks from the bundled JSON files.
2. Ingest or simulate runs for a benchmark.
3. Evaluate each run.
4. Analyze likely failure modes.
5. Compare summary reports across benchmarks and model versions.
6. Optionally log all metrics to MLflow.

For example:

- Benchmark: `browser_export_report`
- Model A: `gpt-4.1-agent`
- Model B: `claude-sonnet-browser`
- Prompt versions: `p3` and `p4`
- Tool interface change: new browser snapshot tool

The stack lets you compare whether the change:

- improved success rate
- reduced wrong-tool errors
- reduced average steps
- increased or decreased latency and cost

---

## Included demo benchmarks

### `browser_export_report_v1`
A browser-style task where the agent must navigate a dashboard, export a report, and mark the workflow complete.

### `compare_pricing_plans_v1`
A mixed text-and-tool task where the agent compares plan options and returns a structured answer.

### `summarize_multi_modal_case_v1`
A task that assumes the agent has text, screenshot metadata, and action history context before producing a structured summary.

These are small but realistic enough to seed dashboards, test schemas, and exercise the evaluator.

---

## How the scoring works

### Exact match scoring

Exact scoring returns:

- success flag
- exact output match flag
- required tools used flag
- required fields present flag
- aggregated score

### Rubric scoring

Rubric scoring returns a normalized score plus criterion-level scores:

- completeness
- correctness
- tool quality
- recovery quality
- efficiency
- format adherence

This rubric is intentionally transparent and deterministic. It does not hide the score behind a black-box judge.

---

## Reproducibility strategy

This repository was designed around reproducible comparisons.

Key choices:

- benchmarks are versioned JSON files checked into source control
- demo runs are generated from deterministic templates
- evaluator logic is explicit and testable
- failure mode analysis is rule-based and explainable
- MLflow logging stores model and prompt configuration alongside metrics

For larger scale use, you can extend this with:

- frozen artifact bundles
- dataset hashing
- exact prompt snapshots
- tool-interface schema versioning
- browser replay traces

---

## How to extend the project

### Add a new benchmark

1. Create a new JSON file in `benchmarks/`
2. Define expected output and evaluator type
3. Load it through `POST /benchmarks/load-defaults` or `POST /benchmarks`

### Add a new evaluator

1. Implement a new evaluator in `backend/app/evaluators.py`
2. Register it in the evaluator dispatch map
3. Add tests in `backend/tests/`

### Add richer failure analysis

You can extend the analyzer to detect:

- tool loops
- brittle selector dependence
- repeated invalid retries
- partial completion before a false success claim
- excessive clarification turns

### Add screenshot or browser-state storage

Right now screenshot references are stored as metadata paths or URLs. You can expand this by adding:

- S3 or GCS artifact storage
- thumbnail generation
- full trace replay pages
- Playwright trace bundle ingestion



---

## Known limitations

This repository is intentionally lightweight enough to run locally, so a few things are simplified:

- screenshot storage is metadata-first rather than binary artifact storage
- browser traces are represented generically rather than as full Playwright bundles
- rubric evaluation is rules-based instead of model-judged
- authentication is not included by default

Those tradeoffs keep the project easy to run while still making the architecture credible and extensible.

## License

MIT
