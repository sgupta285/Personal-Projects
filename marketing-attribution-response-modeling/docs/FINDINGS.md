# Findings

## Overview

This project estimates channel contribution and marketing response curves across paid and owned media using a synthetic but realistic measurement workflow. The goal is not to produce a single true attribution answer. The goal is to compare how different attribution systems behave, quantify diminishing returns, and turn those results into spend decisions.

## Architecture

1. Generate synthetic customer journeys with touchpoints across paid search, paid social, display, affiliate, email, organic search, and direct.
2. Generate a daily spend panel with channel-level conversions and revenue under diminishing returns.
3. Compute first-touch, last-touch, and linear attribution baselines.
4. Fit a logistic regression model on user-level exposure features and estimate removal-effect channel contributions.
5. Fit response curves per channel and estimate marginal conversions per additional dollar.
6. Reallocate budget from lower-return channels to higher-return channels under channel bounds.
7. Publish a dashboard and stakeholder summary.

## Methodology

### Journey-level attribution

Each customer journey contains ordered touchpoints, spend, and a final conversion outcome. Rule-based attribution methods allocate observed conversions and revenue across channels in different ways.

### Model-based attribution

The model-based view uses logistic regression on user-level exposure counts, clicks, and metadata. For each channel, the repo simulates removal by zeroing that channel’s exposure features and measuring the drop in predicted conversion probability. These deltas are aggregated and normalized to observed conversions.

### Response curves and reallocation

The response model fits a diminishing-returns curve per channel using synthetic daily spend data. Marginal return is then used to shift spend from channels with weaker incremental return to those with stronger incremental return, while keeping the total budget constant and respecting minimum and maximum channel bounds.

## Findings

The generated outputs consistently show four patterns:

1. Rule-based views disagree materially.
2. Model-based attribution downweights some last-mile channels.
3. Marginal return decays by channel.
4. Budget should move, not just total spend.

## Reporting outputs

The repo generates:

- attribution comparison tables and charts
- fitted response curve chart
- current versus recommended budget allocation chart
- summary metrics including CAC, ROAS, attributed conversions, and estimated conversion lift from reallocation
- stakeholder summary markdown and dashboard HTML

## Attribution caveats

This project intentionally documents caveats because attribution systems can overstate certainty.

- Rule-based attribution is a reporting convention, not a causal estimate.
- The model-based attribution layer is predictive and still vulnerable to omitted-variable bias.
- Direct and organic traffic often capture intent that was created elsewhere.
- Response curves help with planning but should ideally be validated with holdouts, geo tests, or incrementality experiments.
