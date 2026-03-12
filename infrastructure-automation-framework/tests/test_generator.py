from pathlib import Path

from infraforge.config import load_environment_config, load_service_config
from infraforge.generator import render_environment_bundle, render_helm_assets, render_service_scaffold


def test_render_service_scaffold_writes_expected_files(tmp_path: Path):
    service = load_service_config("examples/configs/service_orders.toml")
    render_service_scaffold(service, tmp_path / "service")
    assert (tmp_path / "service" / "Dockerfile").exists()
    assert (tmp_path / "service" / "deploy/k8s/deployment.yaml").exists()


def test_render_helm_assets_creates_chart_structure(tmp_path: Path):
    service = load_service_config("examples/configs/service_orders.toml")
    env = load_environment_config("examples/configs/env_dev.toml")
    render_helm_assets(service, env, tmp_path / "chart")
    assert (tmp_path / "chart" / "Chart.yaml").exists()
    assert (tmp_path / "chart" / "templates/hpa.yaml").exists()


def test_render_environment_bundle_creates_tfvars(tmp_path: Path):
    env = load_environment_config("examples/configs/env_dev.toml")
    render_environment_bundle(env, tmp_path / "env")
    content = (tmp_path / "env" / "terraform.tfvars").read_text()
    assert 'cluster_name = "platform-dev"' in content
