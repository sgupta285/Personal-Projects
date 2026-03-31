from __future__ import annotations

from collections import Counter
from typing import Any


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.lower().strip().split())
    return str(value).lower().strip()


def score_seed_task(task_payload: dict[str, Any], response: dict[str, Any], gold: dict[str, Any] | None) -> dict[str, Any]:
    if not gold:
        return {"is_seed_task": False, "score": None, "matched": None}

    key = gold.get("key") or next(iter(gold.keys()), None)
    if not key:
        return {"is_seed_task": True, "score": 0.0, "matched": False}

    expected = normalize_text(gold.get(key))
    received = normalize_text(response.get(key))
    matched = expected == received and expected != ""
    return {
        "is_seed_task": True,
        "key": key,
        "expected": expected,
        "received": received,
        "matched": matched,
        "score": 1.0 if matched else 0.0,
    }


def detect_response_anomalies(response: dict[str, Any], time_spent_seconds: int) -> dict[str, Any]:
    flat_values = " ".join(normalize_text(v) for v in response.values())
    too_short = len(flat_values) < 3
    suspiciously_fast = time_spent_seconds < 2
    repeated_token = False
    tokens = flat_values.split()
    if tokens:
        repeated_token = len(set(tokens)) == 1 and len(tokens) >= 3
    return {
        "too_short": too_short,
        "suspiciously_fast": suspiciously_fast,
        "repeated_token": repeated_token,
        "flagged": too_short or suspiciously_fast or repeated_token,
    }


def simple_agreement(values: list[str]) -> dict[str, Any]:
    clean = [normalize_text(v) for v in values if normalize_text(v)]
    if not clean:
        return {"agreement_rate": None, "majority": None, "count": 0}
    counts = Counter(clean)
    majority, majority_count = counts.most_common(1)[0]
    return {
        "agreement_rate": round(majority_count / len(clean), 4),
        "majority": majority,
        "count": len(clean),
        "distribution": dict(counts),
    }
