from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from app.database import init_db
from app.services.compliance import ComplianceService

init_db()
report = ComplianceService().generate_summary()
out = Path("artifacts/compliance_report.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(out)
