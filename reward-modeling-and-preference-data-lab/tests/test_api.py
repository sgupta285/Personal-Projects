from pathlib import Path

from fastapi.testclient import TestClient

DB_FILE = Path('preference_lab.db')
if DB_FILE.exists():
    DB_FILE.unlink()

from app.main import app  # noqa: E402

client = TestClient(app)


def test_end_to_end_api_flow():
    dataset = client.post('/api/datasets', json={
        'name': 'api-dataset',
        'description': 'demo',
        'task_family': 'preference_ranking',
    }).json()

    example = client.post('/api/examples', json={
        'dataset_id': dataset['id'],
        'prompt_text': 'Pick the best summary.',
        'task_type': 'ranking',
        'context': {'domain': 'qa'},
        'metadata': {'domain': 'qa'},
        'candidates': [
            {'label': 'A', 'response_text': 'Candidate one', 'model_name': 'm1', 'metadata': {}},
            {'label': 'B', 'response_text': 'Candidate two', 'model_name': 'm2', 'metadata': {}},
        ],
    }).json()

    ranking = [candidate['id'] for candidate in example['candidates']]
    preference = client.post('/api/preferences', json={
        'example_id': example['id'],
        'annotator_id': 'ann_1',
        'ranking': ranking,
        'notes': 'Looks good',
        'metadata': {'source': 'test'},
    })
    assert preference.status_code == 200

    target = client.get(f"/api/reward-targets/{example['id']}")
    assert target.status_code == 200
    assert target.json()['targets'][str(ranking[0])] == 1.0

    search = client.get('/api/search', params={'dataset_id': dataset['id'], 'query': 'best summary'})
    assert search.status_code == 200
    assert len(search.json()) == 1
