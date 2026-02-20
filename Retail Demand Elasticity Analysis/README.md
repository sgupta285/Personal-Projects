# 📊 Retail Demand Elasticity Analysis

Econometric analysis of price elasticity of demand using OLS log-log regression, panel fixed effects with clustered standard errors, and IV/2SLS with supply-side cost instruments. Estimates own-price and cross-price elasticity matrices, then computes profit-maximizing prices via the Lerner condition. Validated against known true elasticities in synthetic panel data.

---

## Features

- **OLS Log-Log Regression** — constant elasticity estimation with heteroskedasticity-robust standard errors
- **Panel Fixed Effects** — store dummies + seasonal controls, clustered SEs by store
- **IV/2SLS Estimation** — supply-side cost shocks as instruments, first-stage F-test, Durbin-Wu-Hausman endogeneity test
- **Cross-Price Elasticity Matrix** — multivariate log-log identifying substitutes and complements
- **Optimal Pricing** — Lerner condition P* = MC × |ε| / (|ε| - 1) with grid search validation
- **Synthetic Data** — 8 products × 5 stores × 3 years with known true elasticities for method validation
- **Visualization** — demand curves, cross-elasticity heatmaps, revenue optimization, method comparison with 95% CIs

## Architecture

```
Panel Data (store × product × week)
           │
    ┌──────┼──────────────────┐
    ▼      ▼                  ▼
  OLS    Panel FE         IV/2SLS
Log-Log  Clustered SE    Cost Instrument
    │      │                  │
    └──────┼──────────────────┘
           ▼
  Cross-Price Elasticity Matrix
  (substitutes / complements)
           │
           ▼
  Optimal Pricing (Lerner Rule)
  Revenue & profit maximization
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main      # Full analysis
pytest tests/ -v        # Tests
```

## Sample Output

| Product | True ε | OLS ε̂ | Panel FE ε̂ | IV ε̂ |
|---------|--------|--------|------------|-------|
| P00 | -1.80 | -1.73 | -1.78 | -1.85 |
| P01 | -2.20 | -2.08 | -2.15 | -2.24 |
| P02 | -1.50 | -1.42 | -1.48 | -1.53 |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Estimation | statsmodels (OLS, 2SLS), scipy |
| Panel Data | pandas panel operations |
| Optimization | NumPy grid search + Lerner analytical |
| Visualization | matplotlib, seaborn |
| Storage | PostgreSQL |
| CI | GitHub Actions |

## License

MIT
