from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from typing import Any

from app.database import fetch_all


class ComplianceService:
    def generate_summary(self) -> dict[str, Any]:
        rows = fetch_all("SELECT * FROM audit_events ORDER BY id ASC")
        status_counts = Counter(row["status"] for row in rows)
        action_counts = Counter(row["action"] for row in rows)
        actor_counts = Counter(row["actor"] for row in rows)
        denied = [row for row in rows if row["status"] == "denied"]
        return {
            "event_count": len(rows),
            "status_counts": dict(status_counts),
            "action_counts": dict(action_counts),
            "top_actors": actor_counts.most_common(10),
            "denied_access_count": len(denied),
            "evidence_window": {
                "start": rows[0]["ts"] if rows else None,
                "end": rows[-1]["ts"] if rows else None,
            },
        }
