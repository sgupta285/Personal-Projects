from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib


class ConfigError(ValueError):
    pass


@dataclass(slots=True)
class EnvVar:
    key: str
    value: str


@dataclass(slots=True)
class ServiceConfig:
    name: str
    owner: str
    port: int
    replicas: int
    language: str
    health_path: str
    base_image: str
    start_command: str
    cpu_request: str
    memory_request: str
    cpu_limit: str
    memory_limit: str
    namespace: str
    host: str
    image_repository: str
    autoscaling_min: int
    autoscaling_max: int
    target_cpu_utilization: int
    env_vars: list[EnvVar] = field(default_factory=list)


@dataclass(slots=True)
class SecretRef:
    name: str
    provider: str
    path: str


@dataclass(slots=True)
class EnvironmentConfig:
    name: str
    namespace: str
    region: str
    cluster_name: str
    domain: str
    vpc_cidr: str
    public_subnets: list[str]
    private_subnets: list[str]
    secrets: list[SecretRef] = field(default_factory=list)


@dataclass(slots=True)
class Check:
    name: str
    description: str


@dataclass(slots=True)
class AbortCondition:
    name: str
    condition: str


@dataclass(slots=True)
class RolloutConfig:
    service_name: str
    version: str
    owner: str
    environment_name: str
    namespace: str
    cluster: str
    mode: str
    canary_percentages: list[int]
    pause_seconds: int
    success_metric: str
    checks: list[Check] = field(default_factory=list)
    abort_conditions: list[AbortCondition] = field(default_factory=list)


def _load_toml(path: str | Path) -> dict:
    with Path(path).open("rb") as handle:
        return tomllib.load(handle)


def load_service_config(path: str | Path) -> ServiceConfig:
    payload = _load_toml(path)
    for section in ["service", "container", "runtime", "deploy"]:
        if section not in payload:
            raise ConfigError(f"Missing required section: {section}")

    service = payload["service"]
    container = payload["container"]
    runtime = payload["runtime"]
    deploy = payload["deploy"]

    if service["replicas"] < 1:
        raise ConfigError("replicas must be >= 1")
    if deploy["autoscaling_min"] > deploy["autoscaling_max"]:
        raise ConfigError("autoscaling_min cannot exceed autoscaling_max")

    env_vars = [EnvVar(**item) for item in payload.get("env_vars", [])]
    return ServiceConfig(
        name=service["name"],
        owner=service["owner"],
        port=int(service["port"]),
        replicas=int(service["replicas"]),
        language=service["language"],
        health_path=service["health_path"],
        base_image=container["base_image"],
        start_command=container["start_command"],
        cpu_request=runtime["cpu_request"],
        memory_request=runtime["memory_request"],
        cpu_limit=runtime["cpu_limit"],
        memory_limit=runtime["memory_limit"],
        namespace=deploy["namespace"],
        host=deploy["host"],
        image_repository=deploy["image_repository"],
        autoscaling_min=int(deploy["autoscaling_min"]),
        autoscaling_max=int(deploy["autoscaling_max"]),
        target_cpu_utilization=int(deploy["target_cpu_utilization"]),
        env_vars=env_vars,
    )


def load_environment_config(path: str | Path) -> EnvironmentConfig:
    payload = _load_toml(path)
    if "environment" not in payload or "terraform" not in payload:
        raise ConfigError("Environment config must define [environment] and [terraform]")
    env = payload["environment"]
    terraform = payload["terraform"]
    secrets = [SecretRef(**item) for item in payload.get("secrets", [])]
    return EnvironmentConfig(
        name=env["name"],
        namespace=env["namespace"],
        region=env["region"],
        cluster_name=env["cluster_name"],
        domain=env["domain"],
        vpc_cidr=terraform["vpc_cidr"],
        public_subnets=list(terraform["public_subnets"]),
        private_subnets=list(terraform["private_subnets"]),
        secrets=secrets,
    )


def load_rollout_config(path: str | Path) -> RolloutConfig:
    payload = _load_toml(path)
    if not {"service", "environment", "strategy"}.issubset(payload):
        raise ConfigError("Rollout config must define [service], [environment], and [strategy]")

    service = payload["service"]
    environment = payload["environment"]
    strategy = payload["strategy"]

    checks = [Check(**item) for item in payload.get("checks", [])]
    abort_conditions = [AbortCondition(**item) for item in payload.get("abort_conditions", [])]

    return RolloutConfig(
        service_name=service["name"],
        version=service["version"],
        owner=service["owner"],
        environment_name=environment["name"],
        namespace=environment["namespace"],
        cluster=environment["cluster"],
        mode=strategy["mode"],
        canary_percentages=list(strategy.get("canary_percentages", [])),
        pause_seconds=int(strategy["pause_seconds"]),
        success_metric=strategy["success_metric"],
        checks=checks,
        abort_conditions=abort_conditions,
    )
