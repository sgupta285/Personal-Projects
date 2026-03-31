# Reward Modeling and Preference Data Lab

Reward Modeling and Preference Data Lab is a research-oriented preference data system for collecting, versioning, retrieving, and analyzing ranking data used in RLHF-style workflows and reward-model experimentation. It is designed to sit one layer above a labeling platform. Instead of stopping at annotation capture, this project helps answer the next set of questions: what did we collect, which slices are healthy, where do annotators disagree, which examples are reusable, and are the resulting reward targets stable enough to trust.

This repository is intentionally built as a working lab, not a notebook dump. It gives you canonical preference records, dataset snapshots, semantic retrieval over past examples, reward-target generation from human rankings, experiment logging hooks, and analysis endpoints that make the data useful for downstream modeling.

## Why this project matters

A lot of preference-data repositories look complete because they store prompts and rankings. In practice, that is not enough. Teams quickly run into harder operational and research questions:

- Which dataset version produced a given result?
- Are annotators agreeing on the same winners?
- Are some model outputs winning only because of answer position or verbosity?
- How do we find similar historical examples for failure analysis?
- Can we regenerate reward targets consistently after more labels arrive?
- Which experiments used which snapshot of the data?

This project is built to make those questions answerable.

## What the starter implementation includes

### Core data objects
The lab supports the objects described in your project brief:

- **prompt** via `preference_examples.prompt_text`
- **response candidates** via `candidates`
- **rankings** via `preferences.ranking`
- **annotator notes** via `preferences.notes`
- **metadata** at both example and candidate level
- **reward targets** derived from rankings and stored separately

### Storage model
The repository uses SQLite in the starter build so the project is easy to run locally, but the schema is structured in a way that maps cleanly to a PostgreSQL deployment. The README and code are organized so you can swap the storage layer later without rewriting the domain logic.

The canonical tables are:

- `datasets`
- `preference_examples`
- `candidates`
- `preferences`
- `reward_targets`
- `dataset_snapshots`
- `experiment_runs`

### Retrieval layer
The brief called for semantic retrieval across examples with pgvector. In this starter implementation, the retrieval service uses TF-IDF plus cosine similarity so the repo remains runnable without a database extension. The retrieval interface is deliberately isolated in `app/services/retrieval.py`, which makes it straightforward to replace with pgvector later.

### Analysis layer
The lab exposes multiple analysis views out of the box:

- overall dataset counts and activity
- agreement reporting for examples with multiple judgments
- model win-rate and answer-position bias checks
- average candidate length by model
- prompt-sensitivity slices grouped by domain and task type
- reward-target generation from accumulated winner counts

### Experiment logging
The project includes a lightweight experiment tracker that writes structured artifacts to disk and can optionally emit runs to MLflow when an MLflow tracking URI is configured. This keeps the starter repo runnable in a clean local environment while still matching the architecture in the project brief.

## Repository structure

```text
reward-modeling-and-preference-data-lab/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── analytics.py
│   │   ├── mlflow_tracker.py
│   │   ├── repository.py
│   │   ├── retrieval.py
│   │   ├── reward_targets.py
│   │   └── versioning.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── schemas.py
├── data/
│   └── sample_preference_batch.json
├── notebooks/
│   └── preference_data_lab_walkthrough.ipynb
├── scripts/
│   ├── export_snapshot.py
│   ├── run_analysis.py
│   └── seed_demo.py
├── tests/
│   ├── test_analytics.py
│   ├── test_api.py
│   └── test_repository.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── pyproject.toml
└── requirements.txt
```

## System design

### 1. Canonical records first
Every preference judgment is stored against a stable example and stable candidate IDs. This is important because reward targets, analysis reports, and later training exports all depend on reproducible identifiers.

### 2. Snapshots are explicit objects
Instead of vaguely saying a dataset was “the latest version,” the lab freezes a snapshot manifest with a version name and a concrete list of included example IDs. That makes it easy to compare experiment results across dataset versions.

### 3. Retrieval is a first-class workflow
Researchers regularly need to find similar examples when debugging reward targets or reviewing surprising outcomes. The `/api/search` endpoint exists for that reason. It is not decorative.

### 4. Reward targets are materialized
Rather than recomputing targets ad hoc in a notebook, the system stores normalized reward targets in `reward_targets`. That makes downstream training, export, and audit paths much cleaner.

### 5. Analytics live next to the data
The project does not assume every investigation should begin in a notebook. Agreement, bias, and prompt sensitivity are available through API endpoints and reusable service functions.

## Example workflow

A realistic loop with this repository looks like this:

1. Create a dataset for a new preference-collection effort.
2. Add examples with two or more candidate responses.
3. Submit rankings from one or more annotators.
4. Let the lab materialize reward targets after each new judgment.
5. Freeze a snapshot when you want a stable training or evaluation slice.
6. Search for similar examples during failure analysis.
7. Inspect agreement, position bias, and win rates.
8. Log an experiment that references the dataset or a specific snapshot.
9. Export notebooks or artifacts for deeper downstream analysis.

## Local setup

### 1. Clone and create an environment

```bash
git clone <your-repo-url>
cd reward-modeling-and-preference-data-lab
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

The starter configuration uses SQLite so you can run the entire repo locally without external infrastructure.

### 3. Seed demo data

```bash
python scripts/seed_demo.py
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

### 5. Run tests

```bash
pytest -q
```

### 6. Export an analysis summary

```bash
python scripts/run_analysis.py
```

## Docker setup

```bash
cp .env.example .env
docker compose up --build
```

## Key API endpoints

### Create a dataset

```bash
curl -X POST http://localhost:8000/api/datasets   -H "Content-Type: application/json"   -d '{
    "name": "support-chat-preferences",
    "description": "Preference data for support-assistant responses",
    "task_family": "preference_ranking"
  }'
```

### Create an example with candidates

```bash
curl -X POST http://localhost:8000/api/examples   -H "Content-Type: application/json"   -d '{
    "dataset_id": 1,
    "prompt_text": "Rank candidate summaries of this ticket.",
    "task_type": "ranking",
    "context": {"channel": "ticket"},
    "metadata": {"domain": "support"},
    "candidates": [
      {"label": "A", "response_text": "Candidate A", "model_name": "model-a", "metadata": {}},
      {"label": "B", "response_text": "Candidate B", "model_name": "model-b", "metadata": {}}
    ]
  }'
```

### Submit a preference judgment

```bash
curl -X POST http://localhost:8000/api/preferences   -H "Content-Type: application/json"   -d '{
    "example_id": 1,
    "annotator_id": "ann_001",
    "ranking": [1, 2],
    "notes": "A is more specific and less repetitive.",
    "metadata": {"shift": "morning"}
  }'
```

### Freeze a snapshot

```bash
curl -X POST http://localhost:8000/api/snapshots   -H "Content-Type: application/json"   -d '{
    "dataset_id": 1,
    "version_name": "v1.0.0",
    "selection_filter": {"min_preferences": 2}
  }'
```

### Search similar examples

```bash
curl "http://localhost:8000/api/search?dataset_id=1&query=refund%20policy&top_k=3"
```

## Analysis endpoints

- `GET /api/analytics/overview`
- `GET /api/analytics/agreement/{dataset_id}`
- `GET /api/analytics/bias/{dataset_id}`
- `GET /api/analytics/prompt-sensitivity/{dataset_id}`
- `GET /api/reward-targets/{example_id}`

## How reward targets are computed

The starter implementation uses a transparent normalized winner-count method:

1. Count how many times each candidate finished first.
2. Divide by the total number of judgments for the example.
3. Store the resulting per-candidate values as reward targets.

This is intentionally simple. It is easy to inspect and easy to replace with Bradley-Terry, Thurstone, Plackett-Luce, or a learned reward-model target pipeline later.

## Suggested extensions

If you want to push the project further, the next high-leverage improvements would be:

- replace TF-IDF retrieval with pgvector embeddings in PostgreSQL
- add import connectors for data collected from the human-labeling platform
- support pairwise-only and scalar-score feedback tasks
- add annotator calibration and longitudinal quality tracking
- log full experiments to MLflow or Weights & Biases
- export training-ready preference pairs and reward-model datasets
- add bootstrap confidence intervals to the bias and agreement reports

## What I validated while building this repo

- the Python files compile cleanly
- the included test suite passes locally in this environment
- the sample seed script runs successfully
- the analysis export script generates a summary artifact
- the zip is packaged cleanly for direct GitHub upload

## Notes on productionizing

The starter build optimizes for clean local setup and clear architecture. In a production version, I would switch the persistence layer to PostgreSQL, replace the retrieval backend with pgvector, add authentication and RBAC, move artifact storage to object storage, and add asynchronous jobs for large exports and background analysis.
