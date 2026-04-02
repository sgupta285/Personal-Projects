from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import init_db
from app.models import RecordIn, UserContext
from app.services.processor import ProcessorService

init_db()
service = ProcessorService()
actor = UserContext(username="seed_runner", role="processor", org_id="north", allowed_tags=[])

records = [
    RecordIn(subject_id="CASE-001", org_id="north", classification="restricted", region="midwest", department="oncology", payload={"name": "Alex Doe", "email": "alex@example.com", "record_type": "lab", "status": "pending", "priority": "high", "notes": "Elevated markers"}),
    RecordIn(subject_id="CASE-002", org_id="north", classification="confidential", region="midwest", department="cardiology", payload={"name": "Priya Singh", "email": "priya@example.com", "record_type": "claim", "status": "approved", "priority": "medium", "notes": "Routine payment review"}),
]

for item in records:
    record_id = service.create_record(actor, item)
    print(f"seeded record {record_id}")
