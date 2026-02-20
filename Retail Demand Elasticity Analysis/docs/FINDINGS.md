# Retail Demand Elasticity Analysis — Project Findings Report

## 1. Overview

An econometric analysis pipeline estimating own-price and cross-price demand elasticities from retail panel data using OLS log-log regression, panel fixed effects with clustered standard errors, and instrumental variables (2SLS) estimation. Includes cross-price elasticity matrix estimation, profit-maximizing price optimization via the Lerner condition, and validation against known true elasticities embedded in synthetic data.

## 2. Problem Statement

Retailers need to understand how price changes affect demand to set optimal prices. The core econometric challenge is endogeneity: prices are not randomly assigned — firms set prices based on demand conditions, creating a simultaneity bias that makes naive OLS estimates inconsistent. Additionally, estimating the full matrix of cross-price elasticities (how Product A's price affects Product B's demand) is essential for portfolio pricing but requires large panel datasets and careful identification.

## 3. Key Design Choices & Tradeoffs

### Log-Log Specification (Constant Elasticity)
- **Choice**: ln(Q) = α + ε * ln(P) + controls. This gives constant elasticity ε = dQ/Q / dP/P.
- **Tradeoff**: Constant elasticity is restrictive — real demand curves may have varying elasticity at different price points. Linear or semi-log models offer more flexibility but lose the direct elasticity interpretation.
- **Benefit**: Coefficients are directly interpretable as percentage changes. Well-suited for multiplicative demand models common in retail pricing.

### IV/2SLS with Cost Shock Instruments
- **Choice**: Use supply-side cost shocks (e.g., input cost fluctuations) as instruments for price.
- **Tradeoff**: Instrument validity requires the exclusion restriction — cost shocks must affect quantity only through price, not directly. In practice, large cost shocks might signal supply disruptions that independently affect demand.
- **Benefit**: Addresses price endogeneity. First-stage F-statistics validate instrument strength (F > 10 rule of thumb). Durbin-Wu-Hausman test detects whether OLS bias is significant.

### Panel Fixed Effects with Clustered Standard Errors
- **Choice**: Store fixed effects absorb unobserved store-level heterogeneity. Clustered SEs account for within-store correlation.
- **Tradeoff**: Fixed effects remove between-store variation that could help identify elasticity. Clustering reduces effective sample size for inference.
- **Benefit**: Controls for store-specific factors (location, demographics, competition) that correlate with both prices and demand. More conservative (wider) confidence intervals reduce false precision.

### Lerner Pricing Rule for Optimization
- **Choice**: P* = MC × |ε| / (|ε| - 1) for profit-maximizing price under constant elasticity.
- **Tradeoff**: Assumes monopolistic pricing power and constant marginal cost. Ignores competitive response, capacity constraints, and brand positioning.
- **Benefit**: Closed-form solution from first-order conditions. Grid search validation confirms analytical result. Directly translates elasticity estimates into actionable pricing recommendations.

## 4. How to Run

```bash
pip install -r requirements.txt
python -m src.main     # Full pipeline
pytest tests/ -v       # Tests
```

## 5. Known Limitations

1. **Synthetic data** — real retail data has measurement error, stockouts, and endogenous assortment.
2. **Constant elasticity assumption** — linear demand or translog specifications may fit better for some products.
3. **Static analysis** — doesn't model dynamic effects (reference price effects, stockpiling, habit formation).
4. **No demand system** — Almost Ideal Demand System (AIDS) would enforce adding-up and homogeneity restrictions.
5. **Cross-price estimation** — requires all products priced in same market; missing products bias estimates.

## 6. Future Improvements

- **AIDS/Rotterdam demand system** with theoretical consistency constraints
- **Dynamic pricing model** with reference price effects and habit persistence
- **Bayesian hierarchical model** for borrowing strength across products
- **A/B test integration** for causal price effect estimation
- **Heterogeneous elasticities** by customer segment (CRM-linked data)

---

*Report generated for Demand Elasticity Analysis v1.0.0*
