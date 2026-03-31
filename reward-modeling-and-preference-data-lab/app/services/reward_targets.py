from __future__ import annotations

from collections import Counter

from app.services.repository import PreferenceLabRepository


METHOD = "normalized_win_rate"


def compute_reward_targets(repository: PreferenceLabRepository, example_id: int) -> dict[str, float]:
    example = repository.get_example(example_id)
    preferences = [pref for pref in repository.list_preferences() if pref["example_id"] == example_id]
    wins = Counter()
    total = 0
    for pref in preferences:
        ranking = pref["ranking"]
        if ranking:
            wins[str(ranking[0])] += 1
            total += 1

    targets: dict[str, float] = {}
    candidate_ids = [candidate["id"] for candidate in example["candidates"]]
    if total == 0:
        uniform = round(1.0 / len(candidate_ids), 4)
        return {str(candidate_id): uniform for candidate_id in candidate_ids}

    for candidate_id in candidate_ids:
        targets[str(candidate_id)] = round(wins.get(str(candidate_id), 0) / total, 4)
    return targets
