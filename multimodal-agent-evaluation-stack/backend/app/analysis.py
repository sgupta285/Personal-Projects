from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FailureModeResult:
    failure_mode: str
    rationale: str
    signals: dict[str, Any]


def classify_failure(run: dict, evaluation: dict | None = None) -> FailureModeResult:
    trajectory = run.get("trajectory", [])
    final_output = run.get("final_output", {})
    status = run.get("status", "completed")
    success_claimed = run.get("success_claimed", False)
    signals: dict[str, Any] = {
        "status": status,
        "step_count": len(trajectory),
        "failed_steps": sum(1 for step in trajectory if not step.get("success", True)),
        "used_tools": [step.get("tool_name") for step in trajectory],
    }

    if status == "timeout":
        return FailureModeResult(
            failure_mode="timeout",
            rationale="The run ended in timeout before completion.",
            signals=signals,
        )

    if success_claimed and evaluation and not evaluation.get("success", False):
        return FailureModeResult(
            failure_mode="hallucinated_completion",
            rationale="The run claimed success even though the evaluator marked it unsuccessful.",
            signals=signals,
        )

    if any("selector" in (step.get("observation") or "").lower() for step in trajectory):
        return FailureModeResult(
            failure_mode="invalid_state_assumption",
            rationale="The trajectory shows actions based on a page or state assumption that did not hold.",
            signals=signals,
        )

    if any("wrong tool" in (step.get("observation") or "").lower() for step in trajectory):
        return FailureModeResult(
            failure_mode="wrong_tool",
            rationale="The agent used a tool that did not fit the current task or state.",
            signals=signals,
        )

    if trajectory and sum(1 for step in trajectory if not step.get("success", True)) >= 2:
        return FailureModeResult(
            failure_mode="bad_planning",
            rationale="Multiple failed steps suggest poor action sequencing or planning.",
            signals=signals,
        )

    if final_output == {} and len(trajectory) > 0:
        return FailureModeResult(
            failure_mode="unknown",
            rationale="The run executed steps but did not produce a final output.",
            signals=signals,
        )

    return FailureModeResult(
        failure_mode="unknown",
        rationale="No dominant failure mode was detected by the lightweight rules.",
        signals=signals,
    )
