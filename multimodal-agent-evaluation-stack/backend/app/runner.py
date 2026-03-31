from __future__ import annotations

import uuid
from typing import Literal


def _success_browser_run(benchmark_id: str) -> dict:
    return {
        "run_id": str(uuid.uuid4()),
        "benchmark_id": benchmark_id,
        "model_name": "demo-browser-agent",
        "prompt_version": "p1",
        "inputs": {"task": "Export the monthly dashboard report"},
        "final_output": {"status": "exported", "artifact": "report.csv"},
        "trajectory": [
            {"step_index": 1, "tool_name": "navigate", "action": "Open dashboard", "observation": "Dashboard loaded", "latency_ms": 420, "success": True},
            {"step_index": 2, "tool_name": "click", "action": "Open reports tab", "observation": "Reports tab visible", "latency_ms": 180, "success": True},
            {"step_index": 3, "tool_name": "download", "action": "Export monthly report", "observation": "report.csv downloaded", "latency_ms": 920, "success": True},
        ],
        "screenshots": ["artifacts/browser_export_1.png"],
        "browser_state_refs": ["trace://run/browser_export/1"],
        "status": "completed",
        "total_latency_ms": 1520,
        "estimated_cost_usd": 0.07,
        "success_claimed": True,
    }


def _failure_browser_run(benchmark_id: str) -> dict:
    return {
        "run_id": str(uuid.uuid4()),
        "benchmark_id": benchmark_id,
        "model_name": "demo-browser-agent",
        "prompt_version": "p1",
        "inputs": {"task": "Export the monthly dashboard report"},
        "final_output": {},
        "trajectory": [
            {"step_index": 1, "tool_name": "navigate", "action": "Open dashboard", "observation": "Dashboard loaded", "latency_ms": 410, "success": True},
            {"step_index": 2, "tool_name": "click", "action": "Open billing tab", "observation": "Wrong tool path used", "latency_ms": 195, "success": False},
            {"step_index": 3, "tool_name": "click", "action": "Try export button", "observation": "Selector not found on current page", "latency_ms": 255, "success": False},
        ],
        "screenshots": ["artifacts/browser_export_fail.png"],
        "browser_state_refs": ["trace://run/browser_export_fail/1"],
        "status": "completed",
        "total_latency_ms": 1400,
        "estimated_cost_usd": 0.08,
        "success_claimed": True,
    }


def _rubric_run(benchmark_id: str) -> dict:
    return {
        "run_id": str(uuid.uuid4()),
        "benchmark_id": benchmark_id,
        "model_name": "demo-multimodal-agent",
        "prompt_version": "p2",
        "inputs": {"case_id": "demo-42"},
        "final_output": {
            "recommendation": "enterprise",
            "justification": "Includes SSO, audit logs, and admin controls relevant to the task.",
            "format_valid": True,
        },
        "trajectory": [
            {"step_index": 1, "tool_name": "knowledge_lookup", "action": "Read pricing summary", "observation": "Pro lacks audit logs", "latency_ms": 250, "success": True},
            {"step_index": 2, "tool_name": "screenshot_reader", "action": "Inspect admin settings screenshot", "observation": "Enterprise settings include SSO", "latency_ms": 380, "success": True},
            {"step_index": 3, "tool_name": "composer", "action": "Draft structured answer", "observation": "Draft ready", "latency_ms": 600, "success": True},
        ],
        "screenshots": ["artifacts/pricing_compare.png"],
        "browser_state_refs": [],
        "status": "completed",
        "total_latency_ms": 1230,
        "estimated_cost_usd": 0.03,
        "success_claimed": True,
    }


def generate_demo_run(benchmark_id: str, mode: Literal["success", "failure", "rubric"] = "success") -> dict:
    if mode == "success":
        return _success_browser_run(benchmark_id)
    if mode == "failure":
        return _failure_browser_run(benchmark_id)
    return _rubric_run(benchmark_id)
