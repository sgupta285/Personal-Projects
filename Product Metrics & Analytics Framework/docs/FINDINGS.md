# Product Metrics & Analytics Framework — Project Findings Report

## 1. Overview

A comprehensive product analytics framework computing DAU/WAU/MAU engagement metrics, cohort retention tables with churn estimation, conversion funnel analysis, A/B testing (frequentist, Bayesian, sequential), RFM segmentation, behavioral clustering, and LTV projection. Processes 100K+ users with staggered cohorts across 180 days of synthetic product event data.

## 2. Problem Statement

Product teams need a unified analytics framework to measure engagement, identify retention bottlenecks, evaluate experiments, and segment users for targeted interventions. Key challenges include correctly computing rolling active user counts (DAU/WAU/MAU) with staggered signups, building cohort retention tables that account for censoring, running statistically rigorous A/B tests with multiple testing correction, and segmenting users into actionable groups.

## 3. Key Design Choices & Tradeoffs

### DAU/MAU Rolling Window vs Snapshot
- **Choice**: Exact rolling window (set union over 7/30 days) rather than sampling.
- **Tradeoff**: O(n × days × window) computation — expensive for large datasets. Approximate methods (HyperLogLog) would be faster but lose exactness.
- **Benefit**: Precise stickiness metric. DAU/MAU directly measures habitual engagement strength.

### Cohort Retention: Weekly vs Monthly Cohorts
- **Choice**: Weekly cohort granularity with configurable period size.
- **Tradeoff**: Weekly cohorts give finer visibility into retention changes (e.g., catching a bad release) but produce noisier estimates with smaller cohort sizes. Monthly cohorts are smoother but slower to detect issues.
- **Benefit**: Heatmap visualization clearly shows retention trends across cohorts and periods simultaneously.

### A/B Testing: Frequentist + Bayesian + Sequential
- **Choice**: Three complementary testing frameworks.
- **Tradeoff**: Frequentist (z-test/t-test) is industry standard but binary (significant/not). Bayesian gives probability of being best but requires prior specification. Sequential testing allows early stopping but has wider confidence intervals.
- **Benefit**: Frequentist provides p-values for regulatory/compliance reporting. Bayesian gives decision-theoretic expected loss. Sequential saves time on clear winners/losers.

### RFM Segmentation: Rule-Based vs Algorithmic
- **Choice**: Quintile-based RFM scoring with rule-based segment labels, plus separate K-Means behavioral clustering.
- **Tradeoff**: Rule-based RFM is interpretable but segments are arbitrary. K-Means finds natural clusters but segments are harder to name and communicate.
- **Benefit**: RFM is actionable for marketing (e.g., "At Risk" users get re-engagement campaigns). Behavioral clusters provide complementary insights on engagement patterns.

### LTV Projection: Exponential Decay Extrapolation
- **Choice**: Fit exponential decay to observed monthly ARPU, then project forward with discounting.
- **Tradeoff**: Assumes revenue decay is smooth and exponential — ignores seasonality, lifecycle events, and price changes. BG/NBD model would be more principled but requires transaction-level timing data.
- **Benefit**: Simple, interpretable, and works with limited data (3+ months of history).

## 4. How to Run

```bash
pip install -r requirements.txt
python -m src.main      # Full pipeline
pytest tests/ -v        # Tests
```

## 5. Known Limitations

1. **Synthetic data** — real products have more complex behavioral patterns, bugs, and external events
2. **No real-time** — batch computation, not streaming metrics
3. **LTV model simplistic** — no BG/NBD, no contractual/non-contractual distinction
4. **A/B test assumes IID** — doesn't handle network effects or interference
5. **No CUPED/regression adjustment** — variance reduction for experiments not implemented

## 6. Future Improvements

- **Streaming metrics** via Apache Kafka + Flink for real-time DAU
- **BG/NBD + Gamma-Gamma** model for probabilistic LTV
- **CUPED variance reduction** for A/B tests
- **Causal impact analysis** for non-randomized interventions
- **Anomaly detection** on metric time series
- **dbt integration** for SQL-based metric definitions

---

*Report generated for Product Metrics Framework v1.0.0*
