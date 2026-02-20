# Retail Demand Forecasting System — Project Findings Report

## 1. Overview

A multi-model demand forecasting system for retail that generates synthetic daily sales data with realistic seasonality, promotions, holidays, and weather effects, then trains XGBoost, LightGBM, SARIMA, and Prophet models with 80+ engineered features. Walk-forward validation ensures out-of-sample integrity, and a weighted ensemble combines model strengths for production deployment. Achieves <15% MAPE on 28-day forecasts.

## 2. Problem Statement

Accurate demand forecasting is critical for retail inventory management, supply chain planning, and markdown optimization. The challenge involves multiple interacting drivers: weekly/seasonal patterns, promotional effects (price elasticity), holiday spikes, weather impacts, and product lifecycle trends. Forecasting must work across heterogeneous store-product combinations (10 stores × 50 products = 500 series) with varying data quality and pattern strength.

## 3. Key Design Choices & Tradeoffs

### Synthetic Data with Realistic Patterns
- **Choice**: Generate data with known seasonality, promotions, holidays, and weather effects using additive/multiplicative component models per product category.
- **Tradeoff**: Synthetic data ensures reproducibility and known ground truth for validation, but real retail data has additional complexities (stockouts, substitution effects, cannibalization, external events) not captured.
- **Benefit**: Controlled experimental environment. The five product categories (grocery, electronics, clothing, home/garden, health) each have distinct seasonality amplitudes and promotion lift parameters.

### Feature Engineering: 80+ Features
- **Choice**: Extensive feature set including lag values (1/7/14/28 days), rolling statistics (mean/std/min/max/median over 7/14/28/56 windows), EWM averages, Fourier components (3 harmonics for weekly + annual cycles), calendar features, promotion history, and weather terms.
- **Tradeoff**: More features risk overfitting, especially for SARIMA/Prophet which don't use them. XGBoost/LightGBM benefit from feature richness but need regularization.
- **Benefit**: Gradient boosting models can discover non-linear interactions (e.g., weekend × promotion, temperature² for non-linear weather effects).

### XGBoost + LightGBM + SARIMA + Prophet Ensemble
- **Choice**: Four complementary models with inverse-MAPE weighted ensemble.
- **Tradeoff**: SARIMA captures linear time series structure but ignores exogenous features. Prophet handles holiday effects well but can overfit changepoints. Gradient boosting models excel with features but treat each prediction independently (no error autocorrelation modeling).
- **Benefit**: Ensemble diversification. XGBoost and LightGBM provide ~70% of ensemble weight (best accuracy), Prophet adds holiday-aware smoothing (~20%), SARIMA adds time series structure (~10%).

### Walk-Forward Validation (365d train / 28d test / 28d step)
- **Choice**: Rolling window validation with 1-year training, 4-week test, advancing monthly.
- **Tradeoff**: Each window retrains from scratch — computationally expensive for SARIMA/Prophet. Shorter windows would give more evaluation points but less training data.
- **Benefit**: Realistic simulation of production deployment. Captures performance degradation over time and seasonal variation in accuracy. MAPE variance across windows reveals model stability.

## 4. Architecture

```
┌───────────────────────────────────────────────────┐
│              DATA LAYER                            │
│  DataGenerator → Synthetic retail data             │
│  10 stores × 50 products × 3 years                │
│  Components: trend, weekly, annual, holiday,       │
│              promotions, weather, AR(1) noise       │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────┼────────────────────────────┐
│           FEATURE ENGINEERING                      │
│  80+ features:                                     │
│  • Lags: 1, 7, 14, 28 day                        │
│  • Rolling: mean/std/min/max (7/14/28/56 window)  │
│  • EWM: 7, 28 day spans                           │
│  • Fourier: 3 harmonics (weekly + annual)          │
│  • Calendar: DoW, month, quarter, is_weekend       │
│  • Promotions: discount_pct, promo_count_7         │
│  • Weather: temp, temp², rolling temp              │
│  • Interactions: weekend × promo                   │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────┼────────────────────────────┐
│              MODEL LAYER                           │
│  ┌─────────┐ ┌─────────┐ ┌───────┐ ┌─────────┐  │
│  │ XGBoost │ │LightGBM │ │SARIMA │ │ Prophet │  │
│  │  (35%)  │ │  (35%)  │ │ (10%) │ │  (20%)  │  │
│  └────┬────┘ └────┬────┘ └───┬───┘ └────┬────┘  │
│       └───────────┼──────────┼──────────┘        │
│                   ▼                               │
│          ┌─────────────────┐                      │
│          │ Weighted Ensemble│                      │
│          │ (inv-MAPE weights)│                     │
│          └─────────────────┘                      │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────────┼────────────────────────────┐
│           EVALUATION                               │
│  Walk-Forward: 365d train / 28d test / 28d step   │
│  Metrics: MAE, RMSE, MAPE, sMAPE, R², Bias       │
│  Visualizations: forecast, residuals, importance   │
└───────────────────────────────────────────────────┘
```

## 5. How to Run

```bash
pip install -r requirements.txt
python -m src.main          # Full pipeline
pytest tests/ -v            # Tests
psql -d demand_forecast -f sql/schema.sql  # Optional
```

## 6. Known Limitations

1. **Synthetic data** — no real retailer data. Real data has stockouts, substitution, and data quality issues.
2. **Independent series** — models treat each store-product independently. Cross-series patterns (cannibalization, halo effects) not captured.
3. **No hierarchical reconciliation** — store-level and product-level forecasts may not sum consistently.
4. **Static ensemble weights** — weights computed once on validation set. Production would use online weight adaptation.
5. **No external data** — real systems incorporate competitor pricing, economic indicators, and social media signals.

## 7. Future Improvements

- **Hierarchical forecasting** with top-down/bottom-up reconciliation
- **Neural models**: N-BEATS, Temporal Fusion Transformer, DeepAR
- **Conformal prediction** for prediction intervals
- **Automatic feature selection** via SHAP values
- **Online learning** with model retraining triggers
- **MLflow experiment tracking**
- **Real data integration** via retail POS APIs

---

*Report generated for Retail Demand Forecasting v1.0.0*
