from __future__ import annotations

from typing import Any


def flatten_text(output: dict[str, Any]) -> str:
    chunks: list[str] = []
    for value in output.values():
        if isinstance(value, str):
            chunks.append(value)
        elif isinstance(value, list):
            chunks.extend(str(item) for item in value)
        elif isinstance(value, dict):
            chunks.append(str(value))
    return " ".join(chunks).lower()


def keyword_recall(output: dict[str, Any], expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    text = flatten_text(output)
    hits = sum(1 for keyword in expected_keywords if keyword.lower() in text)
    return round(hits / len(expected_keywords), 4)


def hallucination_risk(output: dict[str, Any], input_text: str) -> float:
    text = flatten_text(output)
    source = input_text.lower()
    suspicious_terms = []
    for token in ["sepsis", "fracture", "oncology", "stroke", "surgery", "opioid"]:
        if token in text and token not in source:
            suspicious_terms.append(token)
    base = max(0.0, 1.0 - (0.2 * len(suspicious_terms)))
    return round(base, 4)


def schema_adherence(validation_passed: bool) -> float:
    return 1.0 if validation_passed else 0.0
