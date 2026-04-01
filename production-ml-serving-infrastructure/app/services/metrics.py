from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    "ml_serving_requests_total",
    "Total prediction requests.",
    labelnames=("endpoint", "status"),
)
REQUEST_LATENCY = Histogram(
    "ml_serving_request_latency_seconds",
    "Prediction request latency.",
    labelnames=("endpoint",),
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5),
)
CACHE_COUNTER = Counter(
    "ml_serving_cache_events_total",
    "Cache events.",
    labelnames=("layer", "result"),
)
BATCH_SIZE_HISTOGRAM = Histogram(
    "ml_serving_batch_size",
    "Dynamic batch sizes.",
    buckets=(1, 2, 4, 8, 16, 32, 64),
)
INFERENCE_LATENCY = Histogram(
    "ml_serving_model_inference_seconds",
    "Model inference latency.",
    labelnames=("model_kind",),
    buckets=(0.001, 0.01, 0.05, 0.1, 0.2, 0.5),
)
FALLBACK_COUNTER = Counter(
    "ml_serving_fallback_total",
    "Fallback model usage count.",
)
