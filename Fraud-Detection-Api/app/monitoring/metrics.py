"""
Custom Prometheus metrics for fraud detection monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary

# Prediction metrics
PREDICTION_COUNT = Counter(
    "fraud_predictions_total",
    "Total number of fraud predictions",
    ["result"],  # "fraud" or "legit"
)

PREDICTION_LATENCY = Histogram(
    "fraud_prediction_latency_seconds",
    "Prediction inference latency",
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.5, 1.0],
)

PREDICTION_SCORE = Histogram(
    "fraud_prediction_score",
    "Distribution of fraud scores",
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

# Cache metrics
CACHE_HITS = Counter("fraud_cache_hits_total", "Cache hit count")
CACHE_MISSES = Counter("fraud_cache_misses_total", "Cache miss count")

# Circuit breaker
CIRCUIT_STATE = Gauge(
    "fraud_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half_open)",
)

# Drift
DRIFT_PSI = Gauge("fraud_drift_psi", "Latest PSI drift score")
DRIFT_ALERT = Gauge("fraud_drift_alert_active", "Whether drift alert is active (0/1)")

# Model
MODEL_LOADED = Gauge("fraud_model_loaded", "Whether model is loaded (0/1)")

# Rate limiting
RATE_LIMITED = Counter("fraud_rate_limited_total", "Total rate-limited requests")
