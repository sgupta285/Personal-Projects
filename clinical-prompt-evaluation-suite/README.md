# Clinical Prompt Evaluation Suite

Clinical Prompt Evaluation Suite is a GitHub-ready project for testing, comparing, and operationalizing prompts in healthcare-style workflows where structured outputs, consistency, and reviewability matter.

This repository is intentionally built as an evaluation environment, not a diagnosis engine. The goal is to help a team compare prompt versions against a fixed gold set, track regressions, validate schema adherence, inspect rubric-based quality signals, and export evidence for stakeholders. It is designed around a narrow but realistic workflow: turning raw utilization-review style clinical notes into structured summaries that an operations team can inspect.

## Why this project is worth building

A lot of prompt experimentation happens in spreadsheets, ad hoc notebooks, or one-off playgrounds. That makes it hard to answer basic questions:

- Which prompt version is actually better?
- Did a formatting change improve consistency but hurt completeness?
- Which examples regress when a system prompt changes?
- Are we seeing unsupported claims in sensitive outputs?
- Can we hand reviewers an export they can audit?

This project solves that with a proper backend, a typed output schema, stored datasets, reproducible runs, scoring logic, MLflow experiment logging, and Excel export support.

## Core use case

The included demo workflow focuses on **clinical note summarization for utilization review operations**.

Input:
- raw note text
- request details
- context about symptoms, prior conservative therapy, risk flags, and documentation gaps

Output:
- deterministic structured JSON matching a typed schema
- rubric scores for quality dimensions
- machine-checkable metrics for schema adherence and keyword recall
- run-level aggregates that make prompt comparisons fast

## What is included

### Backend service
- FastAPI API with endpoints for datasets, prompt versions, evaluation runs, and report export
- SQLAlchemy models for datasets, items, prompt versions, runs, and item-level evaluation results
- SQLite by default for easy local startup, with PostgreSQL-compatible SQLAlchemy wiring

### Evaluation harness
- versioned prompt objects
- fixed demo gold set
- deterministic mock provider for local testing
- schema validation with Pydantic
- rubric-based scoring
- heuristic metrics for keyword recall, hallucination risk, and schema adherence
- run-level aggregates

### Experiment tracking
- MLflow logging for run metadata and metrics
- structured run records stored in the database
- notebook for quick local inspection

### Reporting
- Excel export for completed runs
- API endpoint to generate spreadsheet reports
- seed and local execution scripts for demos

## Project structure

```text
clinical-prompt-evaluation-suite/
├── app/
│   ├── api/
│   │   ├── routes_datasets.py
│   │   ├── routes_prompts.py
│   │   ├── routes_reports.py
│   │   └── routes_runs.py
│   ├── evaluators/
│   │   ├── consistency.py
│   │   ├── heuristics.py
│   │   └── rubric.py
│   ├── services/
│   │   ├── dataset_service.py
│   │   ├── evaluation_service.py
│   │   ├── experiment_service.py
│   │   ├── exports.py
│   │   ├── llm_clients.py
│   │   ├── output_validation.py
│   │   ├── prompt_service.py
│   │   └── scoring.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── templates/
│       └── default_prompts.yaml
├── data/
│   ├── sample_clinical_dataset.csv
│   └── sample_clinical_dataset.json
├── notebooks/
│   └── exploratory_analysis.ipynb
├── scripts/
│   ├── export_excel_report.py
│   ├── run_local_eval.py
│   └── seed_demo.py
├── tests/
│   ├── test_mock_provider.py
│   ├── test_scoring.py
│   └── test_validation.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Architecture

The system uses five layers.

### 1. Gold dataset layer
A dataset is stored as:
- workflow name
- description
- individual test items
- expected keywords
- expected output hints
- split and difficulty

This gives you a stable evaluation bed instead of manually pasting examples into a playground.

### 2. Prompt version layer
Each prompt version stores:
- prompt name
- workflow name
- provider
- model name
- schema version
- temperature
- notes

That means you can compare prompt versions over time without losing the context behind why a prompt changed.

### 3. Generation layer
For local development, the repository ships with a deterministic `MockProvider`.

Why this matters:
- tests stay stable
- demos run without API keys
- GitHub viewers can actually boot the project
- you can later swap in OpenAI or Anthropic integration without rewriting the evaluation stack

The provider abstraction lives in `app/services/llm_clients.py`.

### 4. Validation and scoring layer
Every generated output is scored in two ways.

**Schema validation**
- typed validation using Pydantic
- catches malformed or incomplete outputs
- returns field-level issues

**Rubric scoring**
- relevance
- completeness
- clarity
- safety
- overall average

**Heuristic metrics**
- keyword recall
- schema adherence
- hallucination risk
- weighted composite metric

This combination is useful because not every evaluation dimension should be model-judged, and not every dimension can be captured by exact match.

### 5. Reporting and experiment layer
Each run stores:
- provider and model used
- dataset and prompt version
- item-level outputs
- validation results
- rubric scores
- metrics
- run aggregates

The same run is also logged to MLflow, and a spreadsheet export can be generated for review.

## Example workflow

A realistic team loop looks like this:

1. Create or import a gold dataset.
2. Add a new prompt version.
3. Execute the prompt against the entire dataset.
4. Inspect run-level averages.
5. Export the results to Excel for review.
6. Update the prompt and repeat.
7. Compare regressions and gains before shipping the new prompt.

## Local setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd clinical-prompt-evaluation-suite
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

The default setup uses SQLite and the built-in mock provider, so you do not need external API keys just to run the project locally.

### 3. Seed demo data

```bash
make seed
```

This will:
- create tables
- import the demo dataset
- create a baseline prompt version

### 4. Run an evaluation locally

```bash
python scripts/run_local_eval.py
```

You should see a completed run and aggregate metrics printed in the terminal.

### 5. Start the API

```bash
make run
```

Open:
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## API walkthrough

### Create a dataset

`POST /datasets`

Example body:

```json
{
  "name": "my-dataset",
  "workflow_name": "utilization-review-summary",
  "description": "Small benchmark",
  "items": [
    {
      "item_key": "sample-1",
      "input_text": "Member ID: M-1. Encounter date: 2026-01-01. Request for MRI...",
      "expected_output": {
        "requested_service": "Lumbar spine MRI"
      },
      "expected_keywords": ["failed conservative therapy"],
      "difficulty": "medium",
      "split": "test"
    }
  ]
}
```

### Create a prompt version

`POST /prompts`

### Execute a run

`POST /runs`

Example body:

```json
{
  "prompt_version_id": 1,
  "dataset_id": 1
}
```

### Export results

`POST /reports/runs/{run_id}/excel`

That creates an `.xlsx` file in `artifacts/exports/`.

## Docker usage

```bash
docker compose up --build
```

Then seed in another terminal:

```bash
docker compose exec api python scripts/seed_demo.py
docker compose exec api python scripts/run_local_eval.py
```

## Extending the project

### Add a real LLM provider
The repository intentionally keeps OpenAI and Anthropic as guarded extension points. To wire them in:

1. add SDK dependency
2. read API key from environment
3. call the model in `OpenAIProvider` or `AnthropicProvider`
4. parse and validate the returned JSON
5. keep schema validation after generation
6. log model, prompt version, and latency in the same run record

### Add richer scoring
Good next steps:
- compare prompt versions directly
- add reviewer annotations on item results
- support pairwise prompt bake-offs
- add regression thresholds for CI
- cluster failures by error type
- store multiple output samples per prompt for consistency analysis

### Add PostgreSQL
The app already uses SQLAlchemy, so moving from SQLite to PostgreSQL is mostly a configuration change. Update `DATABASE_URL` and run the app with a Postgres container.

## Included demo dataset

The repository ships with a small three-case benchmark in both JSON and CSV form.

Cases include:
- conservative therapy failure before MRI escalation
- insufficient imaging history for repeat CT
- physical therapy extension with neurologic deficit and utilization concerns

These examples are intentionally small so the repo stays easy to run, but the same structure supports much larger gold sets.

## Safety note

This repository is for **prompt evaluation in controlled operational workflows**. It is not intended to diagnose patients, recommend treatment, or replace clinical judgment. The scoring functions here are also deliberately simple and transparent. In production, sensitive workflows should use stronger review controls, better audit trails, policy checks, and domain expert oversight.

## Tests

Run the test suite with:

```bash
make test
```

The current tests cover:
- schema validation
- scoring behavior
- deterministic mock provider behavior

## What makes this repository strong on GitHub

This is not a single notebook or a thin prompt wrapper. It demonstrates:
- practical prompt versioning
- structured evaluation methodology
- typed output validation
- experiment tracking
- exportable review artifacts
- backend engineering discipline
- domain-aware safeguards

That combination makes it a good portfolio project for roles touching applied AI, evaluation systems, healthcare operations tooling, ML platforms, or prompt quality infrastructure.
