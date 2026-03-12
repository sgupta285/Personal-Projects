# Findings

## Overview

This project measures funnel drop-off and evaluates a synthetic conversion experiment in an e-commerce setting.

## Architecture

1. Generate session-level funnel data with device, channel, category, recency, and variant assignment.
2. Expand sessions into event-level records.
3. Load raw tables into SQLite.
4. Run SQL models for stage metrics, experiment cohorts, and segment breakdowns.
5. Compute A/B test results, confidence intervals, power, and MDE.
6. Publish charts, summary artifacts, and a dashboard-ready layer.

## Key observations

The largest leak happens between product page view and cart creation, which is exactly the kind of friction point growth teams usually care about. The treatment improves downstream progression, especially for mobile traffic and for lower-intent acquisition channels.

The experiment is more valuable when read by segment than as a single aggregate number. Some low-friction desktop and direct cohorts improve only slightly, while mobile paid-social traffic shows a more meaningful response.

## Limits

- The underlying data is synthetic.
- The experiment assumes clean randomization and no cross-session interference.
- The analysis is session-based rather than user-lifetime based.
