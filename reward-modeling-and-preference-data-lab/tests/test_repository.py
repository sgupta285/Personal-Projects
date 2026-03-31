from pathlib import Path

import pytest

DB_FILE = Path('preference_lab.db')
if DB_FILE.exists():
    DB_FILE.unlink()

from app.services.repository import PreferenceLabRepository  # noqa: E402
from app.services.reward_targets import compute_reward_targets  # noqa: E402


def seed_example(repo: PreferenceLabRepository):
    import uuid
    dataset = repo.create_dataset(f'test-dataset-{uuid.uuid4().hex[:8]}', 'desc', 'preference_ranking')
    example = repo.create_example(
        dataset_id=dataset['id'],
        prompt_text='Why did retention drop?',
        task_type='ranking',
        context={'channel': 'analysis'},
        metadata={'domain': 'analytics'},
        candidates=[
            {'label': 'A', 'response_text': 'Signal one', 'model_name': 'm1', 'metadata': {}},
            {'label': 'B', 'response_text': 'Signal two', 'model_name': 'm2', 'metadata': {}},
        ],
    )
    return dataset, example


def test_create_and_fetch_example():
    repo = PreferenceLabRepository()
    dataset, example = seed_example(repo)
    fetched = repo.get_example(example['id'])
    assert fetched['dataset_id'] == dataset['id']
    assert len(fetched['candidates']) == 2


def test_reward_targets_follow_win_rate():
    repo = PreferenceLabRepository()
    dataset, example = seed_example(repo)
    winner = example['candidates'][0]['id']
    loser = example['candidates'][1]['id']
    repo.submit_preference(example['id'], 'ann_1', [winner, loser], '', {})
    repo.submit_preference(example['id'], 'ann_2', [winner, loser], '', {})
    targets = compute_reward_targets(repo, example['id'])
    assert targets[str(winner)] == 1.0
    assert targets[str(loser)] == 0.0
