from pathlib import Path

from infraforge.config import load_rollout_config
from infraforge.rollout import generate_rollout_plan
from infraforge.validators import helm_lint_directory, validate_terraform_directory


def test_rollout_plan_generates_expected_phase_count():
    cfg = load_rollout_config("examples/configs/rollout_orders.toml")
    plan = generate_rollout_plan(cfg)
    assert len(plan["phases"]) == 4
    assert plan["phases"][0]["traffic_percent"] == 10


def test_validate_terraform_directory_dry_run_passes():
    results = validate_terraform_directory("examples/terraform/sample-stack", dry_run=True)
    assert any(result.ok for result in results)
    assert all(result.tool for result in results)


def test_helm_lint_directory_structure_check(tmp_path: Path):
    chart = tmp_path / "chart"
    (chart / "templates").mkdir(parents=True)
    (chart / "Chart.yaml").write_text("apiVersion: v2\nname: demo\nversion: 0.1.0\n")
    (chart / "values.yaml").write_text("service:\n  name: demo\n")
    result = helm_lint_directory(chart, dry_run=True)
    assert result.ok
