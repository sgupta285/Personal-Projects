from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.services.analytics import AnalyticsService
from app.services.repository import PreferenceLabRepository

OUT = ROOT / 'artifacts' / 'analysis_summary.json'


def main() -> None:
    repo = PreferenceLabRepository()
    analytics = AnalyticsService(repo)
    datasets = repo.list_datasets()
    if not datasets:
        raise SystemExit('No datasets found. Run python scripts/seed_demo.py first.')
    dataset_id = datasets[0]['id']
    summary = {
        'overview': analytics.overview(),
        'agreement': analytics.agreement_report(dataset_id),
        'bias': analytics.bias_report(dataset_id),
        'prompt_sensitivity': analytics.prompt_sensitivity_report(dataset_id),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
