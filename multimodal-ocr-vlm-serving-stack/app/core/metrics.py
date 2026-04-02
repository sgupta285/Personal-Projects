from prometheus_client import Counter, Gauge, Histogram

JOB_SUBMISSIONS = Counter("ocr_vlm_job_submissions_total", "Total submitted jobs", ["job_type"])
JOB_COMPLETIONS = Counter("ocr_vlm_job_completions_total", "Completed jobs", ["job_type", "status"])
JOB_LATENCY = Histogram("ocr_vlm_job_latency_seconds", "End-to-end job latency", ["job_type"])
BATCH_SIZE = Histogram("ocr_vlm_batch_size", "Observed batch size", buckets=(1, 2, 4, 8, 16))
GPU_MEMORY_USED = Gauge("ocr_vlm_gpu_memory_used_mb", "Estimated GPU memory allocated")
QUEUE_DEPTH = Gauge("ocr_vlm_queue_depth", "Current queue depth")
CACHE_HITS = Counter("ocr_vlm_cache_hits_total", "Cache hits", ["cache_name"])
