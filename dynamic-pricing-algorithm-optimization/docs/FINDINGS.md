# Findings

## Overview

This project builds a pricing engine that predicts demand as a function of price and context, then searches for the profit-maximizing price inside operational guardrails. The workflow is designed to look like a practical pricing science stack for an e-commerce business.

## Methodology

- Synthetic transaction data is generated with product-level demand baselines, elasticity, seasonality, competitor context, promotion depth, and inventory pressure.
- A feature pipeline derives elasticity context such as price index versus base price, competitor gap, inventory pressure, lagged demand, and channel behavior.
- An XGBoost regressor predicts units sold.
- A simulation layer sweeps candidate prices and scores expected revenue and expected gross profit.
- The recommendation engine chooses the best candidate subject to:
  - a floor above cost
  - a maximum increase relative to competitor price
  - a maximum move band relative to current price
  - tighter behavior when inventory is constrained

## Key outcomes

The backtest consistently shows that the largest gains come from a small subset of contexts:
- high-demand periods where current prices are too conservative
- low-inventory contexts where margin protection matters more than volume
- over-discounted items where the current promotion is deeper than required
- cases where current pricing sits materially above competitors and demand is more elastic

The recommendation queue makes those cases easy to review because it includes both the price move and the estimated profit improvement.

## Limitations

- The data is synthetic, so the measured uplift is a pipeline validation signal rather than a business KPI.
- Counterfactual backtesting uses the known synthetic demand function, which is more informative than purely observational data but easier than a real-world environment.
- The fairness logic is rule-based and could be expanded to policy-based pricing segments later.
- The optimizer assumes single-period inventory constraints and does not yet solve multi-day inventory planning.

## Practical interpretation

This setup is useful as a portfolio project because it shows:
- demand modeling rather than only static descriptive analytics
- offline evaluation of pricing decisions rather than raw prediction alone
- operational price guardrails and explanation logic
- an API-ready pricing service that can be integrated into downstream systems
