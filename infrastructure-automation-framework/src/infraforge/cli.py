from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import json

from infraforge.config import load_environment_config, load_rollout_config, load_service_config
from infraforge.generator import render_environment_bundle, render_helm_assets, render_service_scaffold, write_json
from infraforge.rollout import write_rollout_files
from infraforge.validators import helm_lint_directory, validate_terraform_directory


def _print_actions(actions: list[str]) -> None:
    for action in actions:
        print(action)


def cmd_init_service(args: argparse.Namespace) -> int:
    cfg = load_service_config(args.config)
    actions = render_service_scaffold(cfg, args.output, dry_run=args.dry_run)
    _print_actions(actions)
    return 0


def cmd_create_env(args: argparse.Namespace) -> int:
    cfg = load_environment_config(args.config)
    actions = render_environment_bundle(cfg, args.output, dry_run=args.dry_run)
    _print_actions(actions)
    return 0


def cmd_render_helm(args: argparse.Namespace) -> int:
    service_cfg = load_service_config(args.config)
    env_cfg = load_environment_config(args.env)
    actions = render_helm_assets(service_cfg, env_cfg, args.output, dry_run=args.dry_run)
    _print_actions(actions)
    if args.lint:
        result = helm_lint_directory(args.output, dry_run=args.dry_run)
        print(f"{result.tool}: {'ok' if result.ok else 'failed'} - {result.message}")
        return 0 if result.ok else 1
    return 0


def cmd_validate_terraform(args: argparse.Namespace) -> int:
    results = validate_terraform_directory(args.path, dry_run=args.dry_run)
    ok = True
    for result in results:
        print(f"{result.tool}: {'ok' if result.ok else 'failed'} - {result.message}")
        ok = ok and result.ok
    summary = {
        "path": str(Path(args.path).resolve()),
        "ok": ok,
        "results": [asdict(result) for result in results],
    }
    if args.output:
        write_json(args.output, summary)
    return 0 if ok else 1


def cmd_rollout_plan(args: argparse.Namespace) -> int:
    cfg = load_rollout_config(args.config)
    written = write_rollout_files(cfg, args.output)
    for item in written:
        print(f"wrote {item}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    base = Path(args.output)
    base.mkdir(parents=True, exist_ok=True)
    service_cfg = load_service_config("examples/configs/service_orders.toml")
    env_cfg = load_environment_config("examples/configs/env_dev.toml")
    rollout_cfg = load_rollout_config("examples/configs/rollout_orders.toml")
    render_service_scaffold(service_cfg, base / "service-orders")
    render_environment_bundle(env_cfg, base / "env-dev")
    render_helm_assets(service_cfg, env_cfg, base / "helm-orders")
    write_rollout_files(rollout_cfg, base / "rollout-orders")
    validation_output = base / "validation-summary.json"
    terraform_results = validate_terraform_directory("examples/terraform/sample-stack", dry_run=True)
    helm_result = helm_lint_directory(base / "helm-orders", dry_run=True)
    summary = {"terraform": [asdict(item) for item in terraform_results], "helm": asdict(helm_result)}
    validation_output.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"generated demo assets under {base}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="infraforge", description="Infrastructure automation framework")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_service = subparsers.add_parser("init-service", help="Scaffold a new service")
    init_service.add_argument("config")
    init_service.add_argument("--output", required=True)
    init_service.add_argument("--dry-run", action="store_true")
    init_service.set_defaults(func=cmd_init_service)

    create_env = subparsers.add_parser("create-env", help="Create an environment bundle")
    create_env.add_argument("config")
    create_env.add_argument("--output", required=True)
    create_env.add_argument("--dry-run", action="store_true")
    create_env.set_defaults(func=cmd_create_env)

    render_helm = subparsers.add_parser("render-helm", help="Render helm-style manifests")
    render_helm.add_argument("config")
    render_helm.add_argument("--env", required=True)
    render_helm.add_argument("--output", required=True)
    render_helm.add_argument("--dry-run", action="store_true")
    render_helm.add_argument("--lint", action="store_true")
    render_helm.set_defaults(func=cmd_render_helm)

    validate_tf = subparsers.add_parser("validate-terraform", help="Validate terraform directory")
    validate_tf.add_argument("path")
    validate_tf.add_argument("--dry-run", action="store_true")
    validate_tf.add_argument("--output")
    validate_tf.set_defaults(func=cmd_validate_terraform)

    rollout = subparsers.add_parser("rollout-plan", help="Generate rollout plan files")
    rollout.add_argument("config")
    rollout.add_argument("--output", required=True)
    rollout.set_defaults(func=cmd_rollout_plan)

    demo = subparsers.add_parser("demo", help="Generate all sample outputs")
    demo.add_argument("--output", default="examples/generated")
    demo.set_defaults(func=cmd_demo)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
