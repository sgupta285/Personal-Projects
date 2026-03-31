from __future__ import annotations

from typing import Any


def compare_outputs(first: dict[str, Any], second: dict[str, Any]) -> float:
    first_keys = set(first.keys())
    second_keys = set(second.keys())
    key_score = len(first_keys & second_keys) / max(1, len(first_keys | second_keys))

    first_summary = str(first.get("summary", "")).strip().lower()
    second_summary = str(second.get("summary", "")).strip().lower()
    summary_score = 1.0 if first_summary == second_summary else 0.6 if first_summary and second_summary else 0.0
    return round((key_score + summary_score) / 2, 4)
