from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.services.repository import PreferenceLabRepository
from app.services.versioning import build_snapshot_manifest


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit('Usage: python scripts/export_snapshot.py <dataset_id> <version_name>')
    dataset_id = int(sys.argv[1])
    version_name = sys.argv[2]
    repo = PreferenceLabRepository()
    manifest = build_snapshot_manifest(repo, dataset_id=dataset_id)
    snapshot = repo.create_snapshot(dataset_id, version_name, manifest)
    out_path = ROOT / 'artifacts' / f'{version_name}.snapshot.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    main()
