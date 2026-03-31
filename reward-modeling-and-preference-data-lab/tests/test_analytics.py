from pathlib import Path

DB_FILE = Path('preference_lab.db')
if DB_FILE.exists():
    DB_FILE.unlink()

from app.services.analytics import AnalyticsService  # noqa: E402
from app.services.repository import PreferenceLabRepository  # noqa: E402


def test_agreement_and_bias_reports_have_expected_keys():
    repo = PreferenceLabRepository()
    dataset = repo.create_dataset('agreement-set', 'desc', 'preference_ranking')
    example = repo.create_example(
        dataset_id=dataset['id'],
        prompt_text='Compare explanations for churn risk.',
        task_type='ranking',
        context={},
        metadata={'domain': 'support'},
        candidates=[
            {'label': 'A', 'response_text': 'A longer better answer', 'model_name': 'alpha', 'metadata': {}},
            {'label': 'B', 'response_text': 'Short answer', 'model_name': 'beta', 'metadata': {}},
        ],
    )
    a, b = [candidate['id'] for candidate in example['candidates']]
    repo.submit_preference(example['id'], 'ann_1', [a, b], '', {})
    repo.submit_preference(example['id'], 'ann_2', [a, b], '', {})

    analytics = AnalyticsService(repo)
    agreement = analytics.agreement_report(dataset['id'])
    bias = analytics.bias_report(dataset['id'])
    sensitivity = analytics.prompt_sensitivity_report(dataset['id'])

    assert agreement['exact_winner_agreement_rate'] == 1.0
    assert 'position_bias_rate' in bias
    assert sensitivity['segments'][0]['prompt_cluster'] == 'support'
