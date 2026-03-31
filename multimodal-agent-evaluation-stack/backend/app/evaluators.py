from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResult:
    score: float
    success: bool
    metrics: dict[str, Any]


def _required_fields_present(expected_output: dict, actual_output: dict) -> bool:
    required_fields = expected_output.get("required_fields", [])
    return all(field in actual_output and actual_output[field] not in (None, "", []) for field in required_fields)


def _required_tools_used(expected_tools: list[str], trajectory: list[dict]) -> bool:
    used_tools = {step.get("tool_name") for step in trajectory}
    return all(tool in used_tools for tool in expected_tools)


def exact_match_evaluator(expected_output: dict, expected_tools: list[str], actual_output: dict, trajectory: list[dict]) -> EvaluationResult:
    expected_payload = expected_output.get("expected_payload")
    output_matches = True if expected_payload is None else actual_output == expected_payload
    fields_present = _required_fields_present(expected_output, actual_output)
    tools_used = _required_tools_used(expected_tools, trajectory)

    components = [output_matches, fields_present, tools_used]
    score = sum(1.0 for item in components if item) / len(components)
    success = all(components)
    return EvaluationResult(
        score=round(score, 4),
        success=success,
        metrics={
            "output_matches": output_matches,
            "required_fields_present": fields_present,
            "required_tools_used": tools_used,
        },
    )


def rubric_evaluator(expected_output: dict, expected_tools: list[str], actual_output: dict, trajectory: list[dict]) -> EvaluationResult:
    weights = {
        "completeness": 0.25,
        "correctness": 0.25,
        "tool_quality": 0.15,
        "recovery_quality": 0.15,
        "efficiency": 0.10,
        "format_adherence": 0.10,
    }

    completeness = 1.0 if _required_fields_present(expected_output, actual_output) else 0.4
    correctness = 1.0 if expected_output.get("preferred_answer") == actual_output.get("recommendation") else 0.5
    tool_quality = 1.0 if _required_tools_used(expected_tools, trajectory) else 0.5

    had_failure = any(not step.get("success", True) for step in trajectory)
    recovered = had_failure and any(step.get("success", False) for step in trajectory[-2:])
    recovery_quality = 1.0 if (not had_failure or recovered) else 0.3

    step_count = max(len(trajectory), 1)
    efficiency = 1.0 if step_count <= expected_output.get("ideal_max_steps", 4) else 0.6

    format_adherence = 1.0 if actual_output.get("format_valid", True) else 0.3

    metrics = {
        "completeness": completeness,
        "correctness": correctness,
        "tool_quality": tool_quality,
        "recovery_quality": recovery_quality,
        "efficiency": efficiency,
        "format_adherence": format_adherence,
    }
    score = round(sum(metrics[name] * weight for name, weight in weights.items()), 4)
    success = score >= expected_output.get("success_threshold", 0.8)
    return EvaluationResult(score=score, success=success, metrics=metrics)


def dispatch_evaluator(evaluator_type: str, expected_output: dict, expected_tools: list[str], actual_output: dict, trajectory: list[dict]) -> EvaluationResult:
    if evaluator_type == "exact_match":
        return exact_match_evaluator(expected_output, expected_tools, actual_output, trajectory)
    if evaluator_type == "rubric":
        return rubric_evaluator(expected_output, expected_tools, actual_output, trajectory)
    raise ValueError(f"Unsupported evaluator type: {evaluator_type}")
