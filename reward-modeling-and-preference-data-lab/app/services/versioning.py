from __future__ import annotations

from collections import Counter
from typing import Any

from app.services.repository import PreferenceLabRepository


def build_snapshot_manifest(repository: PreferenceLabRepository, dataset_id: int, selection_filter: dict[str, Any] | None = None) -> dict[str, Any]:
    selection_filter = selection_filter or {}
    examples = repository.list_examples(dataset_id=dataset_id)
    if task_type := selection_filter.get("task_type"):
        examples = [example for example in examples if example["task_type"] == task_type]
    if min_preferences := selection_filter.get("min_preferences"):
        pref_counts = Counter(pref["example_id"] for pref in repository.list_preferences(dataset_id=dataset_id))
        examples = [example for example in examples if pref_counts.get(example["id"], 0) >= int(min_preferences)]

    return {
        "dataset_id": dataset_id,
        "selection_filter": selection_filter,
        "example_ids": [example["id"] for example in examples],
        "total_examples": len(examples),
    }
