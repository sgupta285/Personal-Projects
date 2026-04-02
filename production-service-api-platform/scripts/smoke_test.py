import os
import sys
import httpx

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "partner-demo-key")


def main() -> int:
    headers = {"X-API-Key": API_KEY}
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        health = client.get("/health/live")
        if health.status_code != 200:
            print("live probe failed")
            return 1
        response = client.get("/api/v1/orders", headers=headers)
        if response.status_code != 200:
            print(f"orders endpoint failed: {response.status_code}")
            return 1
        print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
