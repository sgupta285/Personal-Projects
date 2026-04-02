from __future__ import annotations

import json
import time
from statistics import mean

from mlprep.config import load_config
from mlprep.logging_utils import configure_logging
from mlprep.pipeline import PreparationPipeline


def main() -> None:
    cfg = load_config()
    logger = configure_logging("artifacts/logs/benchmark.log")
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        PreparationPipeline(cfg.raw, logger).run()
        durations.append(time.perf_counter() - start)
    payload = {
        "runs": len(durations),
        "durations_seconds": [round(value, 4) for value in durations],
        "avg_seconds": round(mean(durations), 4),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
