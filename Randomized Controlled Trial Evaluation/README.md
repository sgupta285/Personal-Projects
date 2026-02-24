# 🧪 Randomized Controlled Trial Evaluation

Comprehensive RCT evaluation framework: intent-to-treat (diff-in-means, Lin adjustment, CUPED), LATE via Wald estimator and 2SLS under non-compliance, and heterogeneous treatment effects (subgroup CATE, causal forest T-learner, GATES, BLP). Full diagnostics: covariate balance, Lee attrition bounds, Fisher permutation inference, and multiple testing correction. Validated against known ATE, LATE, and CATEs in synthetic trial data.

---

## Features

- **ITT / ATE Estimation** — Difference-in-means (Neyman), Lin (2013) regression adjustment (fully interacted demeaned covariates, HC2), CUPED pre-experiment variance reduction, non-parametric bootstrap CIs, Fisher randomization inference
- **LATE / 2SLS** — Wald ratio estimator with delta-method SE, manual 2SLS with covariates and corrected SEs, first-stage diagnostics (F-stat, partial R², Staiger-Stock threshold), Hausman endogeneity test (control function approach), compliance type analysis (complier/always-taker/never-taker shares)
- **Heterogeneity** — Subgroup CATE by age/severity/gender, interaction regression with moderator identification, causal forest T-learner with cross-fitting, GATES quintile analysis (Chernozhukov et al. 2018), BLP heterogeneity test, CLAN profiling of most/least affected
- **Diagnostics** — Covariate balance table (SMD, joint F-test), attrition analysis with Lee (2009) trimming bounds, multiple testing correction (Bonferroni, Holm, Benjamini-Hochberg FDR), power analysis

## Architecture

```
RCT Data (5K subjects, 3 compliance types)
      │
  ┌───┼────────────────────────────┐
  ▼   ▼         ▼            ▼     ▼
 ITT  LATE    Hetero-     Diag-  Robust-
(DiM) (2SLS)  geneity    nostics  ness
 Lin  Wald    CATE       Balance  Boot-
CUPED Hausman Forest     Lee      strap
              GATES      Bounds   Fisher
              BLP        MHT
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main      # Full pipeline
pytest tests/ -v        # 40+ tests
```

## Sample Output

```
Method                          Est      SE     p-val  VarRed   |Err|
─────────────────────────────────────────────────────────────────────
Difference-in-Means (ITT)     +2.31   0.324   <.0001    0.0%   0.19
Lin Regression Adjustment     +2.38   0.278   <.0001   26.4%   0.12
CUPED                         +2.35   0.289   <.0001   20.3%   0.15
Wald (Ratio) LATE             +2.95   0.412    0.0003    —     0.25
2SLS (Manual) LATE            +3.02   0.385    0.0001    —     0.18
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| ATE/ITT | NumPy, statsmodels OLS (HC2) |
| IV/2SLS | Manual 2SLS with SE correction |
| Causal Forest | scikit-learn RandomForest T-learner |
| Diagnostics | scipy stats, statsmodels |
| Visualization | matplotlib, seaborn |
| CI | GitHub Actions |

## License

MIT
