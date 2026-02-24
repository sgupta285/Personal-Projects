# Randomized Controlled Trial Evaluation — Project Findings Report

## 1. Overview

A comprehensive RCT evaluation framework implementing intent-to-treat analysis (difference-in-means, Lin regression adjustment, CUPED), local average treatment effect estimation via two-stage least squares under non-compliance, and heterogeneous treatment effect discovery (subgroup CATE, interaction regression, causal forest T-learner, GATES, BLP test). Includes RCT diagnostics (covariate balance, attrition/Lee bounds, multiple testing), validated against known true ATE, LATE, and CATEs in synthetic data with four compliance types.

## 2. Problem Statement

RCTs are the gold standard for causal inference, but real trials face complications: non-compliance (subjects don't follow assignment), attrition (subjects drop out non-randomly), and effect heterogeneity (treatment helps some more than others). This framework addresses each challenge with appropriate estimators and provides tools to detect, diagnose, and report these issues.

## 3. Key Design Choices & Tradeoffs

### Wald vs 2SLS for LATE Estimation
- **Wald (ratio) estimator**: LATE = ITT_Y / ITT_D. Simple, transparent, exact for single binary instrument.
- **2SLS with covariates**: Adds covariate control for efficiency. First stage: D = π₀ + π₁Z + π₂X + v. Second stage: Y = β₀ + τD̂ + β₁X + ε.
- **Tradeoff**: Wald is simpler and doesn't require correct specification of covariate relationships. 2SLS is more efficient (tighter CIs) but the SE correction for using predicted D̂ instead of actual D is critical — naive Stage 2 SEs are wrong.
- **Benefit**: Both target the same LATE parameter under monotonicity (no defiers). 2SLS gives ~10-20% tighter confidence intervals with good covariates.

### Compliance Framework: Monotonicity Assumption
- **Choice**: Assume no defiers (D(1)=0, D(0)=1 never occurs). Only compliers, always-takers, never-takers.
- **Tradeoff**: Monotonicity is untestable. If defiers exist, LATE is not identified. In medical trials, defiers are rare; in policy settings (e.g., job training), they may be more common.
- **Benefit**: Clean identification of LATE as the complier-specific ATE. Observable compliance shares: P(AT) = P(D=1|Z=0), P(NT) = P(D=0|Z=1), P(C) = 1 - P(AT) - P(NT).

### T-Learner for CATE vs S-Learner or R-Learner
- **Choice**: Separate models for μ₁(x) and μ₀(x) with cross-fitting.
- **Tradeoff**: T-learner can be biased when treatment/control groups have different covariate distributions (not an issue in RCTs). R-learner (Robinson 1988 residualization) would be more robust in observational settings. S-learner (single model with T as feature) tends to regularize heterogeneity toward zero.
- **Benefit**: T-learner is natural for RCTs with balanced groups. Cross-fitting prevents overfitting in CATE estimates. Feature importance directly interpretable as CATE drivers.

### GATES + BLP for Heterogeneity Testing
- **Choice**: Chernozhukov et al. (2018) framework — sort by predicted CATE, form quintiles, test for monotonic increase.
- **Tradeoff**: GATES is a post-hoc analysis (not pre-registered), so must be interpreted carefully. Quintile boundaries are data-dependent.
- **Benefit**: Omnibus heterogeneity test (F-test across quintiles). CLAN profiles most/least affected groups for targeting. BLP β₁ tests whether ML-predicted CATEs actually predict variation in true effects.

### Lee Bounds for Attrition
- **Choice**: Trim the less-attrited group to equalize attrition rates, compute upper/lower bounds.
- **Tradeoff**: Bounds can be wide if differential attrition is large. Assumes monotonicity of attrition with respect to treatment.
- **Benefit**: Partial identification — even under worst-case attrition selection, the ATE lies within the bounds. No parametric assumptions.

## 4. How to Run

```bash
pip install -r requirements.txt
python -m src.main      # Full pipeline
pytest tests/ -v        # 40+ tests
```

## 5. Known Limitations

1. **Synthetic data** — real RCTs have more complex non-compliance patterns, clustering, and outcome measurement error
2. **T-learner heterogeneity** — may underperform R-learner or causal forests with honest splitting in observational settings
3. **No doubly-robust estimation** — AIPW (augmented IPW) would combine propensity weighting with outcome modeling for robustness
4. **Single instrument** — no overidentification tests; multiple instruments would allow Sargan/Hansen J-test
5. **No Bayesian estimation** — posterior distributions on ATE/LATE would provide richer uncertainty quantification

## 6. Future Improvements

- **AIPW/doubly-robust estimator** for semiparametric efficiency
- **Generalized random forest** (grf package equivalent) with honest splitting and variance estimation
- **Bayesian causal inference** with posterior on ATE, LATE, and CATE
- **Sensitivity analysis** for monotonicity violation (partial identification bounds)
- **Mediation analysis** for mechanism decomposition
- **Multiple hypothesis testing** with pre-analysis plans and sequential monitoring

---

*Report generated for RCT Evaluation Framework v1.0.0*
