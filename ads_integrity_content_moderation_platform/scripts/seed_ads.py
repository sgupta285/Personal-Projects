import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "backend" / "worker" / "data" / "seed_ads.json"
API_URL = "http://localhost:8000/api/v1/ads"


def main() -> None:
    ads = json.loads(SAMPLE_PATH.read_text())
    with httpx.Client(timeout=10.0) as client:
        for ad in ads:
            response = client.post(API_URL, json=ad)
            response.raise_for_status()
            print("Seeded:", response.json()["id"], "-", ad["title"])


if __name__ == "__main__":
    main()
