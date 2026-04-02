import statistics
import time

import httpx

BASE_URL = "http://localhost:8000"
ITERATIONS = 25


def main() -> None:
    timings = []
    with httpx.Client(timeout=5.0) as client:
        for _ in range(ITERATIONS):
            start = time.perf_counter()
            response = client.get(f"{BASE_URL}/api/v1/restaurants", params={"city": "Chicago", "sort_by": "rating"})
            response.raise_for_status()
            timings.append((time.perf_counter() - start) * 1000)
    print(f"avg_ms={statistics.mean(timings):.2f}")
    print(f"p95_ms={sorted(timings)[int(ITERATIONS * 0.95) - 1]:.2f}")


if __name__ == "__main__":
    main()
