# 📊 Minimum Wage Employment Effects

Causal inference analysis of minimum wage increases on employment using four econometric methods: difference-in-differences with two-way fixed effects, event study dynamic treatment effects, synthetic control with placebo inference, and regression discontinuity design. Validated against known true effects in synthetic state-quarter panel data (50 states × 40 quarters).

---

## Features

- **Two-Way Fixed Effects DiD** — State + time FEs, clustered SEs at state level, multiple outcomes (employment, wages, hours, restaurant/teen employment)
- **Event Study** — Dynamic treatment effects with leads/lags, pre-trend F-test for parallel trends diagnostics, visual treatment timing
- **Synthetic Control** — NNLS-weighted donor pool matching pre-treatment trajectory, post/pre RMSPE ratio, permutation-based placebo inference
- **Regression Discontinuity** — Local linear/polynomial at minimum wage threshold, bandwidth sensitivity analysis
- **Robustness Battery** — Placebo time/outcome tests, trimmed sample, covariate balance (SMD < 0.10), control state jackknife
- **Parallel Trends Testing** — Formal pre-treatment trend test, event study visual diagnostic

## Architecture

```
State-Quarter Panel (50 × 40)
          │
  ┌───────┼──────────────────────┐
  ▼       ▼          ▼           ▼
 DiD    Event     Synthetic     RDD
(TWFE)  Study     Control    (Threshold)
  │       │          │           │
  └───────┼──────────┼───────────┘
          ▼
  Robustness & Falsification
  (5 checks: placebo, balance, etc.)
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main      # Full analysis
pytest tests/ -v        # 25+ tests
```

## Sample Output

| Outcome | DiD Estimate | True Effect | p-value |
|---------|-------------|-------------|---------|
| Employment Rate | -0.0118 | -0.0120 | 0.003 |
| Avg Wage | +0.52 | +0.54 | <0.001 |
| Avg Hours | -0.61 | -0.65 | 0.012 |
| Restaurant Emp | -0.0210 | -0.0216 | 0.001 |
| Teen Emp | -0.0295 | -0.0300 | <0.001 |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Estimation | statsmodels OLS (clustered SE, FE) |
| Synthetic Control | scipy NNLS optimization |
| RDD | Local polynomial regression |
| Visualization | matplotlib, seaborn |
| CI | GitHub Actions |

## License

MIT
