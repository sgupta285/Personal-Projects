# 📊 Product Metrics & Analytics Framework

Comprehensive product analytics: DAU/WAU/MAU engagement, cohort retention heatmaps, conversion funnels, A/B testing (frequentist + Bayesian + sequential), RFM segmentation, behavioral clustering, and LTV projection. Processes 100K+ users across 180 days of synthetic SaaS product data.

---

## Features

- **Engagement Metrics** — DAU/WAU/MAU time series, DAU/MAU stickiness ratio, session depth/duration, L7/L28 activity scores, feature adoption rates with power-user analysis
- **Retention Analysis** — Weekly/monthly cohort retention tables, Day-N retention curves, exponential churn estimation, retention by segment (platform, country, variant)
- **Funnel Analysis** — Stage-by-stage conversion rates, drop-off identification, bottleneck detection, segment-level funnel comparison
- **A/B Testing** — Frequentist (z-test proportions, Welch's t-test continuous), Bayesian (Beta-Binomial posterior, P(B>A), expected loss), sequential testing (O'Brien-Fleming boundaries), power analysis, Bonferroni/Holm multiple testing correction
- **User Segmentation** — RFM scoring (quintile-based) with rule-based segment labels (Champions, Loyal, At Risk, Hibernating, etc.), K-Means behavioral clustering
- **Revenue & LTV** — ARPU/ARPPU, paying user rate, AOV, 30d/90d windowed LTV, projected LTV via exponential decay extrapolation with discounting

## Architecture

```
  Event Data (100K users × 180 days)
         │
  ┌──────┼──────────────────────────────┐
  │      │      │       │       │       │
  ▼      ▼      ▼       ▼       ▼       ▼
 DAU   Cohort  Funnel  A/B     RFM   Revenue
 WAU   Reten-  Analy-  Test-   Seg-    LTV
 MAU   tion    sis     ing     ments
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main      # Full pipeline
pytest tests/ -v        # 30+ tests
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Metrics | pandas, NumPy |
| Statistics | scipy, statsmodels |
| Clustering | scikit-learn K-Means |
| Visualization | matplotlib, seaborn |
| Storage | PostgreSQL |
| CI | GitHub Actions |

## License

MIT
