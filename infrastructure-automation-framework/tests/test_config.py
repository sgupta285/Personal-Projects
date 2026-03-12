from pathlib import Path

import pytest

from infraforge.config import ConfigError, load_environment_config, load_service_config


def test_load_service_config_reads_expected_fields():
    cfg = load_service_config("examples/configs/service_orders.toml")
    assert cfg.name == "orders-api"
    assert cfg.port == 8080
    assert cfg.autoscaling_max == 5
    assert len(cfg.env_vars) == 2


def test_invalid_service_config_rejects_bad_autoscaling(tmp_path: Path):
    config_path = tmp_path / "bad.toml"
    config_path.write_text(
        """[service]
name = "bad"
owner = "x"
port = 8080
replicas = 1
language = "python"
health_path = "/health"

[container]
base_image = "python:3.11"
start_command = "python app.py"

[runtime]
cpu_request = "100m"
memory_request = "128Mi"
cpu_limit = "200m"
memory_limit = "256Mi"

[deploy]
namespace = "dev"
host = "bad.dev"
image_repository = "example/bad"
autoscaling_min = 3
autoscaling_max = 1
target_cpu_utilization = 70
"""
    )
    with pytest.raises(ConfigError):
        load_service_config(config_path)


def test_environment_config_loads_secrets():
    cfg = load_environment_config("examples/configs/env_dev.toml")
    assert cfg.name == "dev"
    assert cfg.secrets[0].name == "database_url"
