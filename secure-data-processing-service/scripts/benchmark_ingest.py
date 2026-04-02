from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import time

from app.database import init_db
from app.models import RecordIn, UserContext
from app.services.processor import ProcessorService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    args = parser.parse_args()

    init_db()
    service = ProcessorService()
    actor = UserContext(username="bench_runner", role="processor", org_id="north", allowed_tags=[])

    start = time.perf_counter()
    for i in range(args.records):
        service.create_record(
            actor,
            RecordIn(
                subject_id=f"bench-{i}",
                org_id="north",
                classification="restricted",
                region="midwest",
                department="ops",
                payload={
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "record_type": "transaction",
                    "status": "queued",
                    "priority": "low",
                    "notes": "batch benchmark",
                },
            ),
        )
    elapsed = time.perf_counter() - start
    throughput = args.records / elapsed if elapsed else 0
    print({"records": args.records, "seconds": round(elapsed, 3), "throughput_rps": round(throughput, 1)})


if __name__ == "__main__":
    main()
