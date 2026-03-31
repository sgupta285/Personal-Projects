from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from statistics import mean

from app.services.repository import PreferenceLabRepository


class AnalyticsService:
    def __init__(self, repository: PreferenceLabRepository) -> None:
        self.repository = repository

    def overview(self) -> dict:
        return self.repository.overview_counts()

    def agreement_report(self, dataset_id: int) -> dict:
        grouped = self.repository.preferences_grouped_by_example(dataset_id)
        multiple = {example_id: prefs for example_id, prefs in grouped.items() if len(prefs) >= 2}
        exact_matches = 0
        pairwise_total = 0
        pairwise_matches = 0
        winner_distribution = Counter()

        for prefs in multiple.values():
            winners = [pref["winner_candidate_id"] for pref in prefs if pref["winner_candidate_id"] is not None]
            if winners:
                winner_distribution.update(map(str, winners))
                if len(set(winners)) == 1:
                    exact_matches += 1
            for left, right in combinations(prefs, 2):
                shared = list(set(left["ranking"]) & set(right["ranking"]))
                for a, b in combinations(shared, 2):
                    left_prefers = left["ranking"].index(a) < left["ranking"].index(b)
                    right_prefers = right["ranking"].index(a) < right["ranking"].index(b)
                    pairwise_total += 1
                    if left_prefers == right_prefers:
                        pairwise_matches += 1

        total_examples = len(multiple)
        return {
            "dataset_id": dataset_id,
            "total_examples_with_multiple_judgments": total_examples,
            "exact_winner_agreement_rate": round(exact_matches / total_examples, 4) if total_examples else 0.0,
            "pairwise_agreement_rate": round(pairwise_matches / pairwise_total, 4) if pairwise_total else 0.0,
            "winner_distribution": dict(winner_distribution),
        }

    def bias_report(self, dataset_id: int) -> dict:
        examples = self.repository.list_examples(dataset_id=dataset_id)
        preferences = self.repository.list_preferences(dataset_id=dataset_id)
        winner_lookup = Counter(str(pref["winner_candidate_id"]) for pref in preferences if pref["winner_candidate_id"] is not None)
        model_wins = Counter()
        lengths = defaultdict(list)
        first_position_wins = 0
        first_position_total = 0

        for example in examples:
            for idx, candidate in enumerate(example["candidates"]):
                model_name = candidate.get("model_name") or "unknown"
                lengths[model_name].append(len(candidate["response_text"].split()))
                if winner_lookup.get(str(candidate["id"])):
                    model_wins[model_name] += winner_lookup[str(candidate["id"])]
                if idx == 0:
                    first_position_total += winner_lookup[str(candidate["id"])]
            if example["candidates"]:
                top_candidate_id = str(example["candidates"][0]["id"])
                first_position_wins += winner_lookup.get(top_candidate_id, 0)

        total_model_wins = sum(model_wins.values()) or 1
        model_win_rates = {model: round(wins / total_model_wins, 4) for model, wins in model_wins.items()}
        avg_lengths = {model: round(mean(values), 2) for model, values in lengths.items()}
        position_bias_rate = round(first_position_wins / first_position_total, 4) if first_position_total else 0.0
        return {
            "dataset_id": dataset_id,
            "model_win_rates": model_win_rates,
            "position_bias_rate": position_bias_rate,
            "average_candidate_length_by_model": avg_lengths,
        }

    def prompt_sensitivity_report(self, dataset_id: int) -> dict:
        examples = self.repository.list_examples(dataset_id=dataset_id)
        preferences = self.repository.list_preferences(dataset_id=dataset_id)
        win_counts = Counter(str(pref["winner_candidate_id"]) for pref in preferences if pref["winner_candidate_id"] is not None)
        segments = defaultdict(list)

        for example in examples:
            domain = str(example["metadata"].get("domain", "general"))
            candidate_wins = [win_counts.get(str(candidate["id"]), 0) for candidate in example["candidates"]]
            if not candidate_wins:
                continue
            ordered = sorted(candidate_wins, reverse=True)
            margin = ordered[0] - ordered[1] if len(ordered) > 1 else ordered[0]
            key = (domain, example["task_type"])
            segments[key].append(margin)

        report_segments = []
        for (domain, task_type), margins in sorted(segments.items()):
            report_segments.append(
                {
                    "prompt_cluster": domain,
                    "task_type": task_type,
                    "average_margin": round(sum(margins) / len(margins), 4),
                    "examples": len(margins),
                }
            )
        return {"dataset_id": dataset_id, "segments": report_segments}
