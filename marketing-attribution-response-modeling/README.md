# Marketing Attribution & Response Modeling

A marketing science project that estimates channel contribution across paid and owned media, fits spend response curves, and recommends budget reallocations under diminishing returns.

This repository is designed to look and behave like a compact analytics deliverable for a growth, marketing science, or measurement team. It generates synthetic customer journeys and channel spend data, benchmarks rule-based attribution methods, adds a model-based attribution layer, fits response curves per channel, and produces a stakeholder summary with budget recommendations.

## What is included

- synthetic touchpoint and spend datasets
- first-touch, last-touch, and linear attribution baselines
- model-based attribution using logistic regression removal effects
- spend response curve fitting for paid and owned channels
- budget reallocation analysis under diminishing returns
- generated dashboard HTML and stakeholder summary
- SQL reference models and reproducible bootstrap flow
- validation tests for attribution totals and optimizer constraints

## Project structure

```text
marketing-attribution-response-modeling/
├── data/
├── docs/
├── dashboard/
├── notebooks/
├── reports/
├── scripts/
├── sql/
├── src/marketing_attribution/
└── tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
make bootstrap
```

Open the generated dashboard at `dashboard/index.html`.

## Main outputs

Running `make bootstrap` creates:

- `data/raw/touchpoints.csv`
- `data/raw/daily_spend.csv`
- `data/processed/journeys.csv`
- `data/processed/channel_attribution_baselines.csv`
- `data/processed/model_attribution.csv`
- `data/processed/response_curves.csv`
- `data/processed/budget_reallocation.csv`
- `reports/summary_metrics.json`
- `reports/*.png`
- `dashboard/index.html`
- `docs/STAKEHOLDER_SUMMARY.md`

## Methods

### Attribution baselines

The project starts with three common rules:

- first-touch attribution
- last-touch attribution
- linear attribution

These are not causal. They are benchmark views of how credit moves depending on the chosen reporting rule.

### Model-based attribution

The repo also fits a logistic regression model on user-level exposure features built from the touchpoint table. Channel contribution is estimated with a removal-effect approach: for each channel, the model recomputes conversion probability with that channel's exposure set to zero, then aggregates the probability drop. The resulting contributions are normalized back to observed conversions so the output is easier to compare with baseline methods.

### Response modeling

Response curves are fit per channel on synthetic daily spend panels using a diminishing-returns functional form:

`conversions = alpha * (1 - exp(-beta * spend))`

The fitted curves are used to estimate marginal return and guide budget movement from saturated channels toward more productive ones.

## Caveats

- The data is synthetic and intended for systems design and measurement workflow demonstration.
- The model-based attribution layer is descriptive, not causal.
- Direct and organic traffic can carry strong last-mile correlation, which is why the project keeps caveats visible in the generated summary.
- The budget optimizer relies on fitted response curves, so its quality depends on the realism of those curves.

## Commands

```bash
make bootstrap   # generate data, fit models, build reports
make test        # run validation tests
make clean       # remove generated artifacts
```
