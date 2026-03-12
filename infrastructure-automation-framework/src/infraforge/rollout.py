from __future__ import annotations

from pathlib import Path
from textwrap import dedent
import json

from infraforge.config import RolloutConfig


def generate_rollout_plan(cfg: RolloutConfig) -> dict:
    phases = []
    for percent in cfg.canary_percentages:
        phases.append(
            {
                "traffic_percent": percent,
                "pause_seconds": cfg.pause_seconds,
                "success_metric": cfg.success_metric,
                "action": f"shift traffic to {percent}% for {cfg.service_name}:{cfg.version}",
            }
        )
    return {
        "service": cfg.service_name,
        "version": cfg.version,
        "owner": cfg.owner,
        "environment": cfg.environment_name,
        "namespace": cfg.namespace,
        "cluster": cfg.cluster,
        "strategy": cfg.mode,
        "prechecks": [{"name": item.name, "description": item.description} for item in cfg.checks],
        "phases": phases,
        "abort_conditions": [{"name": item.name, "condition": item.condition} for item in cfg.abort_conditions],
    }


def rollout_markdown(cfg: RolloutConfig, plan: dict) -> str:
    prechecks = "\n".join(f"- **{item['name']}**: {item['description']}" for item in plan["prechecks"])
    phases = "\n".join(f"- {phase['action']} and observe for {phase['pause_seconds']}s" for phase in plan["phases"])
    aborts = "\n".join(f"- **{item['name']}**: {item['condition']}" for item in plan["abort_conditions"])
    return dedent(
        f"""# Rollout plan for {cfg.service_name}

- version: {cfg.version}
- environment: {cfg.environment_name}
- namespace: {cfg.namespace}
- strategy: {cfg.mode}

## Prechecks
{prechecks}

## Rollout phases
{phases}

## Abort conditions
{aborts}

## Success metric
{cfg.success_metric}
"""
    )


def write_rollout_files(cfg: RolloutConfig, output_dir: str | Path) -> list[str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = generate_rollout_plan(cfg)
    markdown_path = output_dir / "rollout-plan.md"
    json_path = output_dir / "rollout-plan.json"
    markdown_path.write_text(rollout_markdown(cfg, plan).rstrip() + "\n")
    json_path.write_text(json.dumps(plan, indent=2) + "\n")
    return [str(markdown_path), str(json_path)]
