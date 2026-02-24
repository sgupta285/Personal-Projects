# Minimum Wage Employment Effects — Project Findings Report

## 1. Overview

A causal inference analysis of minimum wage increases on employment outcomes using four complementary econometric methods: two-way fixed effects difference-in-differences (DiD) with clustered standard errors, event study dynamic treatment effects, synthetic control method with placebo inference, and regression discontinuity design. Validated against known true treatment effects embedded in synthetic state-quarter panel data (50 states × 40 quarters).

## 2. Problem Statement

Estimating the causal effect of minimum wage increases on employment is one of the most studied questions in labor economics. The fundamental challenge is selection bias: states that raise their minimum wage may differ systematically from those that don't. This project implements multiple identification strategies, each exploiting different sources of variation and relying on different assumptions, to triangulate a credible causal estimate.

## 3. Key Design Choices & Tradeoffs

### Two-Way Fixed Effects DiD
- **Choice**: State fixed effects absorb time-invariant state heterogeneity; time fixed effects absorb common shocks (business cycle, policy changes). SEs clustered at the state level.
- **Tradeoff**: Requires parallel trends assumption — absent treatment, treated and control states would have followed the same trajectory. Violated if states with different trends self-select into treatment.
- **Benefit**: Industry-standard method. Clustering corrects for serial correlation within states (Bertrand et al., 2004). Estimates multiple outcome variables simultaneously.

### Event Study (Dynamic DiD)
- **Choice**: Estimate separate treatment effects for each quarter relative to policy change, with pre-treatment leads serving as a parallel trends diagnostic.
- **Tradeoff**: Requires many pre-periods for a convincing pre-trend test. Power decreases for individual period estimates vs. pooled DiD.
- **Benefit**: Visualizes treatment dynamics — can detect anticipation effects (pre-trend), on-impact effects, and fade-out. Pre-trend F-test provides formal parallel trends evidence.

### Synthetic Control
- **Choice**: NNLS-weighted combination of control states to match treated state's pre-treatment trajectory. Placebo tests via permutation across all states.
- **Tradeoff**: Works for a single treated unit (or must be applied separately to each). Requires good pre-treatment fit. Inference is non-standard (rank-based p-value from placebos).
- **Benefit**: No parallel trends assumption on the aggregate. Transparent about which control states contribute. Visual display of counterfactual is compelling for policy audiences.

### Regression Discontinuity
- **Choice**: Local linear regression at the minimum wage threshold with varying bandwidths.
- **Tradeoff**: RDD estimates a local average treatment effect (LATE) at the cutoff — may not generalize to larger wage increases. Bandwidth selection involves bias-variance tradeoff.
- **Benefit**: Minimal assumptions (continuity of potential outcomes at cutoff). Bandwidth sensitivity analysis reveals robustness.

## 4. How to Run

```bash
pip install -r requirements.txt
python -m src.main      # Full analysis
pytest tests/ -v        # Tests
```

## 5. Known Limitations

1. **Synthetic data** — real minimum wage studies deal with spillovers, migration, and anticipation effects not fully modeled here.
2. **TWFE with staggered adoption** — recent literature shows TWFE DiD can be biased with heterogeneous treatment effects under staggered rollout. Modern estimators (Callaway & Sant'Anna, de Chaisemartin & d'Haultfoeuille) would be more appropriate.
3. **RDD running variable** — minimum wage as a running variable is discrete, not continuous, which weakens RDD assumptions.
4. **No general equilibrium** — doesn't model firm exit/entry, price pass-through, or labor-labor substitution.

## 6. Future Improvements

- **Staggered DiD estimators** (Callaway-Sant'Anna, Sun-Abraham)
- **Bounds analysis** (Lee bounds for partial identification)
- **Bayesian structural time series** for synthetic control uncertainty
- **Geographic regression discontinuity** (border county pairs)
- **Heterogeneity analysis** via causal forests

---

*Report generated for Minimum Wage Analysis v1.0.0*
