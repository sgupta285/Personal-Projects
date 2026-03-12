from __future__ import annotations

from pathlib import Path
from textwrap import dedent
import json

from infraforge.config import EnvironmentConfig, ServiceConfig


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def render_service_scaffold(cfg: ServiceConfig, output_dir: str | Path, dry_run: bool = False) -> list[str]:
    output_dir = Path(output_dir)
    files = {
        output_dir / "README.md": service_readme(cfg),
        output_dir / ".env.example": env_example(cfg),
        output_dir / "Dockerfile": dockerfile(cfg),
        output_dir / "app/main.py": app_main(cfg),
        output_dir / "deploy/k8s/deployment.yaml": deployment_yaml(cfg),
        output_dir / "deploy/k8s/service.yaml": service_yaml(cfg),
        output_dir / ".github/workflows/service-ci.yml": service_ci(cfg),
    }
    actions = []
    for path, content in files.items():
        actions.append(f"render {path}")
        if not dry_run:
            _write(path, content)
    return actions


def render_environment_bundle(cfg: EnvironmentConfig, output_dir: str | Path, dry_run: bool = False) -> list[str]:
    output_dir = Path(output_dir)
    files = {
        output_dir / "terraform.tfvars": terraform_tfvars(cfg),
        output_dir / "namespace.yaml": namespace_yaml(cfg),
        output_dir / "secrets.md": secrets_markdown(cfg),
        output_dir / "README.md": environment_readme(cfg),
    }
    actions = []
    for path, content in files.items():
        actions.append(f"render {path}")
        if not dry_run:
            _write(path, content)
    return actions


def render_helm_assets(service: ServiceConfig, environment: EnvironmentConfig, output_dir: str | Path, dry_run: bool = False) -> list[str]:
    output_dir = Path(output_dir)
    files = {
        output_dir / "Chart.yaml": chart_yaml(service),
        output_dir / "values.yaml": values_yaml(service, environment),
        output_dir / "templates/deployment.yaml": deployment_yaml(service),
        output_dir / "templates/service.yaml": service_yaml(service),
        output_dir / "templates/configmap.yaml": configmap_yaml(service, environment),
        output_dir / "templates/hpa.yaml": hpa_yaml(service),
    }
    actions = []
    for path, content in files.items():
        actions.append(f"render {path}")
        if not dry_run:
            _write(path, content)
    return actions


def write_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def service_readme(cfg: ServiceConfig) -> str:
    return dedent(
        f"""# {cfg.name}

Scaffolded by Infrastructure Automation Framework.

- owner: {cfg.owner}
- port: {cfg.port}
- namespace: {cfg.namespace}
- host: {cfg.host}

## Local run

```bash
uvicorn app.main:app --reload --port {cfg.port}
```
"""
    )


def env_example(cfg: ServiceConfig) -> str:
    lines = [f"{item.key}={item.value}" for item in cfg.env_vars]
    return "\n".join(lines) if lines else "APP_ENV=dev"


def dockerfile(cfg: ServiceConfig) -> str:
    return dedent(
        f"""FROM {cfg.base_image}

WORKDIR /app
COPY app ./app
RUN pip install --no-cache-dir fastapi uvicorn
EXPOSE {cfg.port}
CMD ["sh", "-c", "{cfg.start_command}"]
"""
    )


def app_main(cfg: ServiceConfig) -> str:
    return dedent(
        f"""from fastapi import FastAPI

app = FastAPI(title=\"{cfg.name}\")


@app.get(\"/health\")
def health() -> dict:
    return {{\"status\": \"ok\", \"service\": \"{cfg.name}\"}}


@app.get(\"/\")
def root() -> dict:
    return {{\"service\": \"{cfg.name}\", \"owner\": \"{cfg.owner}\"}}
"""
    )


def deployment_yaml(cfg: ServiceConfig) -> str:
    env_lines = "\n".join(
        f"        - name: {item.key}\n          value: \"{item.value}\"" for item in cfg.env_vars
    )
    if not env_lines:
        env_lines = "        []"
    return dedent(
        f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {cfg.name}
  namespace: {cfg.namespace}
spec:
  replicas: {cfg.replicas}
  selector:
    matchLabels:
      app: {cfg.name}
  template:
    metadata:
      labels:
        app: {cfg.name}
    spec:
      containers:
        - name: {cfg.name}
          image: {cfg.image_repository}:latest
          ports:
            - containerPort: {cfg.port}
          resources:
            requests:
              cpu: {cfg.cpu_request}
              memory: {cfg.memory_request}
            limits:
              cpu: {cfg.cpu_limit}
              memory: {cfg.memory_limit}
          env:
{env_lines}
          readinessProbe:
            httpGet:
              path: {cfg.health_path}
              port: {cfg.port}
          livenessProbe:
            httpGet:
              path: {cfg.health_path}
              port: {cfg.port}
"""
    )


def service_yaml(cfg: ServiceConfig) -> str:
    return dedent(
        f"""apiVersion: v1
kind: Service
metadata:
  name: {cfg.name}
  namespace: {cfg.namespace}
spec:
  selector:
    app: {cfg.name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: {cfg.port}
"""
    )


def chart_yaml(cfg: ServiceConfig) -> str:
    return dedent(
        f"""apiVersion: v2
name: {cfg.name}
type: application
version: 0.1.0
appVersion: \"latest\"
"""
    )


def values_yaml(service: ServiceConfig, environment: EnvironmentConfig) -> str:
    env_block = "\n".join(f"  - name: {item.key}\n    value: \"{item.value}\"" for item in service.env_vars)
    if not env_block:
        env_block = "  []"
    return dedent(
        f"""service:
  name: {service.name}
  namespace: {environment.namespace}
  port: {service.port}
  image: {service.image_repository}:latest
  host: {service.host}
resources:
  requests:
    cpu: {service.cpu_request}
    memory: {service.memory_request}
  limits:
    cpu: {service.cpu_limit}
    memory: {service.memory_limit}
autoscaling:
  minReplicas: {service.autoscaling_min}
  maxReplicas: {service.autoscaling_max}
  targetCPUUtilizationPercentage: {service.target_cpu_utilization}
env:
{env_block}
"""
    )


def configmap_yaml(service: ServiceConfig, environment: EnvironmentConfig) -> str:
    return dedent(
        f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {service.name}-config
  namespace: {environment.namespace}
data:
  APP_ENV: \"{environment.name}\"
  LOG_FORMAT: \"json\"
  SERVICE_OWNER: \"{service.owner}\"
"""
    )


def hpa_yaml(service: ServiceConfig) -> str:
    return dedent(
        f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service.name}
  namespace: {service.namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {service.name}
  minReplicas: {service.autoscaling_min}
  maxReplicas: {service.autoscaling_max}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {service.target_cpu_utilization}
"""
    )


def namespace_yaml(cfg: EnvironmentConfig) -> str:
    return dedent(
        f"""apiVersion: v1
kind: Namespace
metadata:
  name: {cfg.namespace}
  labels:
    environment: {cfg.name}
    region: {cfg.region}
"""
    )


def terraform_tfvars(cfg: EnvironmentConfig) -> str:
    pub = ", ".join(f'\"{x}\"' for x in cfg.public_subnets)
    priv = ", ".join(f'\"{x}\"' for x in cfg.private_subnets)
    return dedent(
        f"""environment = \"{cfg.name}\"
namespace = \"{cfg.namespace}\"
region = \"{cfg.region}\"
cluster_name = \"{cfg.cluster_name}\"
vpc_cidr = \"{cfg.vpc_cidr}\"
public_subnets = [{pub}]
private_subnets = [{priv}]
"""
    )


def secrets_markdown(cfg: EnvironmentConfig) -> str:
    lines = [f"- `{item.name}` via `{item.provider}` at `{item.path}`" for item in cfg.secrets]
    joined = "\n".join(lines) if lines else "- No secrets defined"
    return f"# Secrets for {cfg.name}\n\n{joined}\n"


def environment_readme(cfg: EnvironmentConfig) -> str:
    return dedent(
        f"""# {cfg.name} environment

- namespace: {cfg.namespace}
- region: {cfg.region}
- cluster: {cfg.cluster_name}
- domain: {cfg.domain}
- vpc cidr: {cfg.vpc_cidr}
"""
    )


def service_ci(cfg: ServiceConfig) -> str:
    return dedent(
        f"""name: service-ci

on:
  push:
  pull_request:

jobs:
  test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t {cfg.name}:ci .
"""
    )
