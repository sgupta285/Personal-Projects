# Causal Inference with Difference-in-Differences

A policy evaluation repository for panel-data causal inference using difference-in-differences as the primary design, with event-study diagnostics, placebo checks, and a synthetic-control fallback when the usual parallel-trends story starts to look shaky.

This project was built around a practical workflow rather than a single regression table. The point is to move from raw panel data to a defensible analysis package that shows the baseline estimate, checks the identifying assumptions, visualizes treatment dynamics over time, and offers a second design when the treated and control groups do not move together before treatment.

## What this repo does

- generates a realistic sample panel dataset with policy adoption, heterogeneous treatment effects, and a small number of intentionally problematic treated units
- estimates a two-way fixed-effects difference-in-differences model with clustered standard errors
- runs a parallel-trends diagnostic on the pre-period
- runs a placebo treatment test by shifting treatment into the pre-period
- builds an event study to show how treatment effects evolve over time
- computes a synthetic control for a treated unit using non-negative donor weights
- writes an analysis summary, markdown report, HTML report, and plots to the `artifacts/` directory
- includes an R `fixest` replication script so the same design can be re-run in a more econometrics-native toolchain
- includes a small Monte Carlo benchmark so the repo is not just a one-off notebook

## Why the repository is structured this way

The README source material for this project was concise but clear. It called for:

- panel-data policy evaluation
- difference-in-differences as the main design
- parallel-trends testing
- synthetic controls when parallel trends fail
- event-study analysis for dynamic effects
- a Python and R toolchain using `statsmodels`, `fixest`, `pandas`, and `matplotlib`

That led to a repository built around a reproducible command-line workflow instead of a dashboard or API surface. There is no fake product layer here. The work is centered on estimation, diagnostics, and reporting.

## Repository layout

```text
causal-inference-difference-in-differences/
├── configs/
│   └── default.yaml
├── data/
│   └── sample/
├── artifacts/
│   ├── benchmarks/
│   ├── plots/
│   └── reports/
├── notebooks/
├── r/
│   └── fixest_replication.R
├── scripts/
│   ├── bootstrap.sh
│   ├── run_benchmark.sh
│   └── run_sample_analysis.sh
├── src/
│   └── did_lab/
│       ├── cli.py
│       ├── config.py
│       ├── data.py
│       ├── diagnostics.py
│       ├── estimators.py
│       ├── pipeline.py
│       └── reporting.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Core workflow

### 1. Sample data generation

The sample panel generator produces a balanced panel with:

- unit fixed effects
- macro and seasonal time patterns
- a covariate that drifts over time
- treated and untreated units
- a common treatment adoption period for treated units
- heterogeneous treatment effects tied to unit characteristics
- a small number of treated units with pre-trend violations so the diagnostics actually have something to catch

This keeps the repo honest. The diagnostics are not decorative. In some simulated runs they pass, and in others they flag exactly the kind of issue that would force a design rethink in a real policy evaluation.

### 2. Baseline DiD

The baseline estimator is a two-way fixed-effects regression with:

- unit fixed effects
- time fixed effects
- a treatment interaction term `ever_treated × post`
- clustered standard errors at the unit level

The implementation lives in `src/did_lab/estimators.py` and uses `statsmodels` directly so the model matrix and inference path stay explicit.

### 3. Parallel-trends diagnostic

The pre-period diagnostic regresses the outcome on:

- treatment-group indicator
- centered time trend
- treatment-group-by-time interaction
- observed covariate

The coefficient on the interaction is the pre-trend slope difference. That is the simplest useful first pass when reviewing whether treated and control units were already moving apart before treatment.

### 4. Placebo test

The placebo test shifts treatment into the pre-period and re-estimates the DiD model. If that shifted treatment produces a strong signal, the original design deserves more skepticism.

### 5. Event study

The event study creates relative-time indicators around treatment and estimates the dynamic treatment path with the period just before treatment omitted as the reference point. The resulting plot makes it much easier to inspect:

- whether there are visible pre-trends
- how quickly the treatment effect shows up
- whether the effect grows, decays, or stabilizes over time

### 6. Synthetic-control fallback

When the treated and untreated groups fail to look comparable in the pre-period, the repo provides a synthetic-control fallback for a treated unit.

The implementation:

- chooses untreated donor units
- optimizes non-negative donor weights that sum to one
- minimizes pre-period mean squared error
- compares treated-unit post-period outcomes with the weighted synthetic control

This is intentionally kept small and transparent. It is meant to be understandable and easy to extend, not buried in black-box abstractions.

## Local setup

### Option 1: plain Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### Option 2: bootstrap script

```bash
./scripts/bootstrap.sh
```

### Option 3: Docker

```bash
docker build -t did-lab .
docker run --rm -v "$(pwd)":/app did-lab
```

### Option 4: Docker Compose

```bash
docker compose up --build
```

## How to run

### Generate the sample dataset

```bash
python -m did_lab.cli --config configs/default.yaml generate-sample
```

### Run the full analysis

```bash
python -m did_lab.cli --config configs/default.yaml run-analysis
```

This writes:

- `artifacts/analysis_summary.json`
- `artifacts/reports/policy_report.md`
- `artifacts/reports/policy_report.html`
- `artifacts/plots/group_trends.png`
- `artifacts/plots/event_study.png`
- `artifacts/plots/synthetic_control.png`

### Run the Monte Carlo benchmark

```bash
python -m did_lab.cli --config configs/default.yaml benchmark
```

This writes a JSON summary to:

- `artifacts/benchmarks/benchmark_results.json`

### Convenience scripts

```bash
./scripts/run_sample_analysis.sh
./scripts/run_benchmark.sh
```

## Configuration

The project is driven by `configs/default.yaml`.

Key parameters include:

- number of units and periods
- treatment share
- treatment start period
- treatment effect size
- number of units that violate parallel trends
- number of pre-periods to use in the trend diagnostic
- placebo shift length
- benchmark replication count

You can swap in a new config without touching the code.

## R replication path

The repo is runnable in Python, but it also includes an R script using `fixest` for a more standard econometrics workflow.

```bash
Rscript r/fixest_replication.R data/sample/panel.csv
```

The R script runs:

- a fixed-effects DiD model
- an event-study style specification via `sunab()`

That gives a useful cross-check between the Python workflow and an R-first causal inference stack.

## Testing

Run the test suite with:

```bash
pytest
```

The tests cover:

- sample data generation shape and summary
- positive treatment recovery in the DiD estimator
- event-study output shape
- synthetic-control weight normalization
- placebo and parallel-trends diagnostic outputs

## Linting

```bash
ruff check src tests
```

## Benchmarking

The benchmark is a lightweight Monte Carlo loop. It is not meant to be a paper-quality simulation study, but it is useful for checking:

- average recovered treatment effect
- share of runs that are statistically significant
- share of runs where the pre-trend check passes

That makes the repo more reproducible and gives some signal on estimator behavior under the synthetic data generator used here.

## Artifacts and reports

The output directory is designed to be immediately useful in a portfolio or working analysis context.

### JSON summary

Machine-readable summary for downstream tooling.

### Markdown report

Quick to read in GitHub and easy to diff in pull requests.

### HTML report

Simple polished artifact that can be shared without asking someone to open a notebook.

### Plots

- treated vs control average trends
- event-study coefficients
- synthetic-control treated vs weighted donor path

## Design choices

### Why `statsmodels` instead of a larger causal library?

The README source for this project pointed to `statsmodels` and `fixest`, and that fit the scope well. This repo is trying to make the identifying logic visible, not hide it inside a large estimation framework.

### Why synthetic control for a single treated unit?

That is the cleanest way to keep the fallback interpretable and portable. A larger implementation with staggered adoption, matrix completion, or generalized synthetic control would add a lot of machinery that the source spec did not ask for.

### Why a CLI instead of a notebook-only repo?

Notebook-only causal projects are hard to test and easy to break quietly. The CLI makes the analysis reproducible from a fresh clone, while still leaving room for notebooks if someone wants to add more exploratory work.

## License

MIT


