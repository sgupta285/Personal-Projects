# Customer Churn Prediction & Intervention

A production-style churn intelligence system that predicts which SaaS accounts are likely to churn, explains the main drivers behind those predictions, and recommends action tiers for retention teams.

This repository follows a realistic local-first workflow:
- generate synthetic SaaS customer data
- build a customer feature table with SQL-friendly logic
- train an XGBoost churn model
- compute account-level SHAP explanations
- map churn scores to intervention actions
- serve predictions through FastAPI
- review model outcomes in a Streamlit dashboard

## Why this project exists

The goal is not only to classify churn. The goal is to give a revops, lifecycle, or customer success team something operational:
- a scored account queue
- prioritized retention actions
- explanations for each account
- evaluation metrics that matter in top-of-queue workflows

## Architecture

```text
Synthetic events -> feature pipeline -> XGBoost model -> SHAP explanations
                         |                    |
                         v                    v
                   SQLite / SQL         intervention policy
                         |                    |
                         +------> FastAPI + Streamlit
```

## Repository layout

```text
customer-churn-prediction-intervention/
├── api/
├── artifacts/
├── dashboard/
├── data/
├── docs/
├── notebooks/
├── scripts/
├── sql/
├── src/churnintel/
└── tests/
```

## Included outputs

After `make bootstrap`, the project creates:

- `data/raw/customer_events.csv`
- `data/processed/customer_features.csv`
- `data/churn.db`
- `artifacts/model.json`
- `artifacts/metadata.json`
- `artifacts/metrics.json`
- `artifacts/confusion_matrix.json`
- `artifacts/account_explanations.json`
- `artifacts/top_risk_accounts.csv`
- `docs/screenshots/`

## Quick start

### Option 1: local Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
make bootstrap
make api
```

In another terminal:

```bash
source .venv/bin/activate
make dashboard
```

### Option 2: Docker Compose

```bash
docker compose up --build
```

## API endpoints

- `GET /health`
- `POST /predict`
- `GET /top-risk-accounts?limit=25`
- `GET /intervention-queue?limit=25`
- `GET /account-explanation/{account_id}`

## Example prediction call

```bash
curl -X POST "http://127.0.0.1:8000/predict"   -H "Content-Type: application/json"   -d @data/sample_predict_payload.json
```

## Dashboard

The Streamlit app highlights:
- ROC-AUC, PR-AUC, precision@10%, recall@10%, simulated retention uplift
- top risk intervention queue
- confusion matrix
- churn probability vs account value
- risk by plan tier
- feature relationship exploration

Preview files are generated into `docs/screenshots/` during bootstrap so the repo is presentation-ready even before deployment.

## Testing

```bash
make test
```

## Notes

- The dataset is synthetic by design, but the feature patterns mirror a real SaaS retention setting.
- SQLite is used for local reproducibility, while the storage layer is structured so moving to Postgres is easy.
- The intervention policy is intentionally simple and explainable.

## License 

MIT
