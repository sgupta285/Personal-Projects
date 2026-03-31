from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.services.repository import PreferenceLabRepository
from app.services.reward_targets import METHOD, compute_reward_targets

DATASET_PATH = ROOT / 'data' / 'sample_preference_batch.json'


def main() -> None:
    payload = json.loads(DATASET_PATH.read_text(encoding='utf-8'))
    repo = PreferenceLabRepository()
    dataset = repo.create_dataset(**payload['dataset'])
    example_ids: list[int] = []
    label_lookup: list[dict[str, int]] = []

    for example_payload in payload['examples']:
        example = repo.create_example(
            dataset_id=dataset['id'],
            prompt_text=example_payload['prompt_text'],
            task_type=example_payload['task_type'],
            context=example_payload['context'],
            metadata=example_payload['metadata'],
            candidates=example_payload['candidates'],
        )
        example_ids.append(example['id'])
        label_lookup.append({candidate['label']: candidate['id'] for candidate in example['candidates']})

    for pref in payload['preferences']:
        candidate_ids = [label_lookup[pref['example_index']][label] for label in pref['ranking_labels']]
        repo.submit_preference(
            example_id=example_ids[pref['example_index']],
            annotator_id=pref['annotator_id'],
            ranking=candidate_ids,
            notes=pref['notes'],
            metadata=pref['metadata'],
        )

    for example_id in example_ids:
        targets = compute_reward_targets(repo, example_id)
        repo.upsert_reward_target(example_id, METHOD, targets)

    print(f'Seeded dataset {dataset["name"]} with {len(example_ids)} examples.')


if __name__ == '__main__':
    main()
