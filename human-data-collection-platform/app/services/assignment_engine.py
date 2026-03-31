from __future__ import annotations

from typing import Any


def choose_next_task(tasks: list[dict[str, Any]], prior_assignments: set[int], role: str) -> dict[str, Any] | None:
    eligible = []
    for task in tasks:
        if task["id"] in prior_assignments:
            continue
        if role == "annotator" and task["status"] not in {"open", "in_progress"}:
            continue
        if role == "reviewer" and task["status"] != "pending_review":
            continue
        eligible.append(task)

    if not eligible:
        return None

    def sort_key(task: dict[str, Any]) -> tuple[int, int, int]:
        seed_boost = 0 if task.get("seed_task") else 1
        status_boost = 0 if task.get("status") == "in_progress" else 1
        return (seed_boost, -int(task.get("priority", 50)), status_boost)

    eligible.sort(key=sort_key)
    return eligible[0]
