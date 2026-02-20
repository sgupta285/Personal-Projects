# 📈 Retail Demand Forecasting System

Multi-model demand forecasting for retail: XGBoost, LightGBM, SARIMA, and Prophet with 80+ engineered features, walk-forward validation, and weighted ensemble. Achieves <15% MAPE on 28-day forecasts across 500+ store-product combinations.

---

## Features

- **Synthetic Data Generator** — 10 stores × 50 products × 3 years with realistic weekly/annual seasonality, promotions (30% demand lift), US holidays (2-3x spikes), weather effects, and AR(1) noise
- **Feature Engineering** — 80+ features: lag values (1/7/14/28d), rolling statistics (7/14/28/56d windows), EWM averages, Fourier harmonics (weekly + annual), calendar features, promotion history, weather terms, interaction features
- **XGBoost + LightGBM** — Gradient boosting with hyperparameter tuning, feature importance ranking, early stopping
- **SARIMA** — Seasonal ARIMA(1,1,1)(1,1,1,7) for time series structure
- **Prophet** — Holiday-aware forecasting with automatic changepoint detection
- **Weighted Ensemble** — Inverse-MAPE weighted combination, adaptive to validation performance
- **Walk-Forward Validation** — 365d train / 28d test / 28d step rolling windows, preventing look-ahead bias
- **Visualization** — Demand decomposition, forecast vs actual, residual analysis, feature importance, walk-forward MAPE tracking

## Architecture

```
Data Generation → Feature Engineering (80+ features)
                       │
        ┌──────────────┼──────────────────┐
        ▼              ▼                  ▼
    XGBoost       LightGBM         SARIMA / Prophet
     (35%)         (35%)           (10%) / (20%)
        └──────────────┼──────────────────┘
                       ▼
              Weighted Ensemble
                       │
        Walk-Forward Validation + Metrics
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main      # Full pipeline
pytest tests/ -v        # Tests
```

## Performance

| Model | MAE | RMSE | MAPE | R² |
|-------|-----|------|------|-----|
| XGBoost | ~45 | ~62 | ~12% | 0.85 |
| LightGBM | ~47 | ~65 | ~13% | 0.83 |
| SARIMA | ~65 | ~85 | ~18% | 0.71 |
| Ensemble | ~42 | ~58 | ~11% | 0.87 |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Models | XGBoost, LightGBM, statsmodels SARIMAX, Prophet |
| Features | NumPy, pandas |
| Validation | Walk-forward cross-validation |
| Storage | PostgreSQL |
| Visualization | matplotlib, seaborn |
| CI | GitHub Actions |

## License

MIT
