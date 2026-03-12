# Findings

## Overview

This project models customer churn for a subscription SaaS business using synthetic behavior, support, billing, and sentiment signals. The setup is meant to mirror a practical retention analytics stack rather than a one-off notebook.

## Architecture

1. Synthetic account snapshots are generated with realistic operating signals.
2. A feature pipeline aggregates behavior, support, billing, and lifecycle variables to an account-level table.
3. An XGBoost classifier predicts 60-day churn probability.
4. SHAP is used to explain the strongest positive or negative drivers for top-risk accounts.
5. An intervention layer converts risk into concrete save actions.
6. FastAPI and Streamlit expose the outputs for operational use.

## Methodology

- Label: churn is defined as likely inactivity over the next 60 days.
- Features: recency, engagement change, ticket burden, unresolved issue rate, billing friction, product adoption, onboarding completion, sentiment, contract structure, and revenue context.
- Model family: XGBoost is used for the final model because it handles non-linear interactions well while remaining explainable with SHAP.
- Evaluation: ROC-AUC, PR-AUC, precision at top-k, recall at top-k, confusion matrix, and a simple simulated retention uplift estimate.

## Findings and results

The model is strongest where it should be strongest: the top of the intervention queue. Accounts with a steep decline in activity, unresolved support debt, weak product adoption, negative sentiment, and recent payment failures consistently rise to the top.

Three patterns stand out:

1. **Recency and engagement collapse are the clearest early warnings.** A strong drop in weekly sessions or transactions relative to the prior month is one of the most reliable churn signals.
2. **Support friction compounds adoption weakness.** A high unresolved ticket rate becomes much more dangerous when feature adoption is already low.
3. **Billing stress matters more on lower-commitment contracts.** Monthly plans with payment failures and recent plan volatility are much more fragile than longer-term contracts.

The intervention policy routes human attention toward the accounts where it matters most:
- high-risk, high-value accounts go to CSM outreach
- high-risk, lower-value accounts get save offers or lifecycle outreach
- medium-risk accounts receive education and onboarding reinforcement
- low-risk accounts remain in monitor mode

## Limitations

- The dataset is synthetic, so metrics should be treated as pipeline validation rather than business truth.
- The uplift estimate uses assumed save rates by intervention type rather than measured experiment outcomes.
- SHAP explanations are descriptive, not causal.

## Screenshots

After bootstrap, preview screenshots are generated under `docs/screenshots/`.
