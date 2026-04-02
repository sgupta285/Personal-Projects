from time import perf_counter

from fastapi.testclient import TestClient

from app.main import app


if __name__ == "__main__":
    client = TestClient(app)
    iterations = 100
    start = perf_counter()
    for _ in range(iterations):
        response = client.get("/usage/breakdown", params={"dimension": "feature", "interval": "day"})
        response.raise_for_status()
    elapsed = perf_counter() - start
    print({"iterations": iterations, "total_seconds": round(elapsed, 4), "avg_ms": round((elapsed / iterations) * 1000, 2)})
