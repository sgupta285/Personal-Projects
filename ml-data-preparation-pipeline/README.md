# ML Data Preparation Pipeline

A production-minded data preparation repository for machine learning workflows. The project is built around the scope implied by the uploaded portfolio README: automated validation, schema enforcement, anomaly checks, transformation pipelines, feature engineering, and quality reporting for reproducible model training. The original README frames this work as reducing data quality issues through validation and anomaly detection, handling missing values, outlier treatment, encoding, and scaling with proper train-test separation, and producing dashboards for completeness, distribution shift, and correlation review.

## What this repository includes

- A configurable preprocessing pipeline for tabular ML data
- Automated validation checks for required schema, null thresholds, duplicate keys, and anomalies
- Lightweight expectation handling inspired by Great Expectations style suites
- Feature engineering that runs before preprocessing and remains traceable
- Train-test-safe winsorization, imputation, encoding, and scaling
- Static HTML and JSON quality reports that act as a reproducible dashboard snapshot
- PostgreSQL export for prepared feature tables
- Tests, benchmark tooling, Docker, and CI

## Real-world framing

This repo models the part of ML infrastructure that quietly determines whether downstream models are trustworthy. Most production model issues do not start in the serving layer. They start earlier, when raw data arrives with missing fields, shifted distributions, duplicated entities, or leakage-prone preprocessing. I wanted this repository to feel like the preparation layer a team would actually keep in source control before handing features to training and evaluation jobs.

The pipeline uses a synthetic customer dataset because it makes validation, anomaly detection, and categorical feature handling easy to inspect locally. The implementation is intentionally practical rather than overbuilt. There is one clear path from raw CSV to validated, transformed feature tables and a report that can be reviewed before training.

## README-backed project spec

From the uploaded portfolio README, this project is described as follows:

- **Overview:** a data preparation pipeline supporting ML workflows by handling data validation, quality checks, transformation, and feature engineering so that clean, consistent data reaches training and evaluation.
- **Key results:** reduced data quality issues by 60% through automated validation, schema enforcement, and anomaly detection; built transformation pipelines for missing values, outlier treatment, encoding, and scaling with proper train-test separation; created dashboards monitoring completeness, distribution shifts, and feature correlations.
- **Focus areas:** Data Engineering, ML Pipelines, Data Quality, Feature Engineering, Validation, and ETL.
- **Tech stack:** Python, Pandas, NumPy, scikit-learn, Great Expectations, and PostgreSQL.

## Architecture

```text
raw csv
  -> validation and expectation checks
  -> feature engineering
  -> train/test split
  -> fit preprocessing only on training data
  -> transform train and test consistently
  -> save artifacts and reports
  -> optionally export prepared training features to PostgreSQL
```

## Repository layout

```text
ml-data-preparation-pipeline/
├── configs/
│   ├── expectations.json
│   └── pipeline.yaml
├── data/
│   ├── processed/
│   └── raw/
├── artifacts/
│   ├── logs/
│   ├── models/
│   └── reports/
├── scripts/
│   ├── benchmark_pipeline.py
│   ├── export_to_postgres.py
│   ├── generate_sample_data.py
│   └── run_pipeline.py
├── src/mlprep/
│   ├── cli.py
│   ├── config.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── logging_utils.py
│   ├── pipeline.py
│   ├── postgres.py
│   ├── preprocessing.py
│   ├── reporting.py
│   └── validation.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Core workflow

### 1. Sample data generation

The included dataset generator creates a mixed-type customer churn style dataset with numeric, categorical, and boolean fields. It also injects a few realistic issues:

- missing values in selected columns
- a small number of outliers
- duplicate customer ids

That lets the validation layer produce a meaningful report instead of passing trivially.

### 2. Validation and schema enforcement

The validator checks:

- required columns
- null rate thresholds
- duplicate keys
- simple z-score anomaly counts
- expectation suite rules from `configs/expectations.json`

I kept the expectation file human-readable so it can be edited without touching Python.

### 3. Feature engineering

The pipeline adds a few derived fields before preprocessing:

- `spend_per_session`
- `ticket_rate`
- `engagement_bucket`

These are deliberately simple and auditable. In a real system, this stage would usually be where teams start to overfit or create leakage. That is why the rest of the preprocessing flow is strict about what gets fit on training data only.

### 4. Train-test-safe preprocessing

The preprocessing layer does the following in order:

- split data into train and test sets with a fixed random seed
- winsorize numeric features based on training quantiles
- impute missing numeric values with the training median
- impute missing categorical values with the training mode
- one-hot encode categoricals
- standardize numeric values

The same fitted transformer is then reused for both training and test data and saved as a serialized artifact.

### 5. Dashboard-style reporting

The repository writes:

- an HTML report at `artifacts/reports/data_quality_report.html`
- a JSON summary at `artifacts/reports/pipeline_summary.json`

The report includes:

- validation status table
- missingness snapshot
- train versus test distribution shift summary
- top numeric correlations

This is intentionally a static report rather than a web dashboard because it is easier to archive, compare across runs, and store with model artifacts.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Environment variables

Copy `.env.example` if you want PostgreSQL export.

```bash
cp .env.example .env
```

Relevant variables:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SCHEMA`

## How to run

### Generate sample data

```bash
python scripts/generate_sample_data.py
```

### Run the pipeline

```bash
python scripts/run_pipeline.py
```

or

```bash
mlprep run
```

### Export prepared features to PostgreSQL

```bash
python scripts/export_to_postgres.py
```

or

```bash
mlprep export
```

## Benchmarking

```bash
python scripts/benchmark_pipeline.py
```

This runs the pipeline five times and prints average wall-clock duration.

## Testing

```bash
pytest
```

The included tests cover duplicate-key validation and the basic train-test separation guarantee in the preprocessing stage.

## PostgreSQL notes

The repository includes an export helper that writes the prepared training feature set into a configurable schema and table. `docker-compose.yml` includes a local Postgres service so the export path can be tested without extra setup.

## Docker usage

Build and run the pipeline container:

```bash
docker compose up --build
```

## License

MIT
