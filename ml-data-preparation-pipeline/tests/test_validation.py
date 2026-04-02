from pathlib import Path

import pandas as pd

from mlprep.config import load_config
from mlprep.validation import DataValidator, findings_to_summary


def test_validator_flags_duplicate_keys(tmp_path: Path) -> None:
    cfg = load_config().raw
    df = pd.DataFrame(
        {
            "customer_id": [1, 1],
            "monthly_spend": [10.0, 20.0],
            "sessions_last_30d": [1, 2],
            "avg_session_minutes": [10.0, 12.0],
            "support_tickets": [0, 1],
            "account_age_days": [100, 100],
            "region": ["west", "west"],
            "device_type": ["web", "ios"],
            "plan_tier": ["basic", "pro"],
            "signup_channel": ["organic", "paid"],
            "is_premium": [0, 1],
            "churned": [0, 1],
        }
    )
    findings = DataValidator(cfg).run(df)
    summary = findings_to_summary(findings)
    assert summary["failed"] >= 1
    assert any(f.check == "duplicate_keys" and f.status == "failed" for f in findings)
