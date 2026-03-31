
from __future__ import annotations

from typing import Any


def summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_count": len(result.get("pages", [])),
        "block_count": len(result.get("blocks", [])),
        "section_count": len(result.get("sections", [])),
        "table_count": len(result.get("tables", [])),
        "entity_count": len(result.get("entities", [])),
        "warning_count": len(result.get("warnings", [])),
    }


def compare_revisions(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_summary = summarize_result(left)
    right_summary = summarize_result(right)
    deltas = {}
    for key, old_value in left_summary.items():
        deltas[key] = {
            "from": old_value,
            "to": right_summary[key],
            "delta": right_summary[key] - old_value,
        }
    return deltas
