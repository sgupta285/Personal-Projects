from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(slots=True)
class ValidationResult:
    tool: str
    ok: bool
    message: str


REQUIRED_TERRAFORM_FILES = ["main.tf", "variables.tf", "providers.tf"]


def validate_terraform_directory(path: str | Path, dry_run: bool = False) -> list[ValidationResult]:
    path = Path(path)
    results: list[ValidationResult] = []

    for required in REQUIRED_TERRAFORM_FILES:
        file_path = path / required
        if file_path.exists():
            results.append(ValidationResult("terraform-structure", True, f"found {required}"))
        else:
            results.append(ValidationResult("terraform-structure", False, f"missing {required}"))

    unresolved = []
    for tf_file in path.glob("*.tf"):
        text = tf_file.read_text()
        if "{{" in text or "}}" in text:
            unresolved.append(tf_file.name)
    if unresolved:
        results.append(ValidationResult("template-check", False, f"unresolved placeholders in {', '.join(unresolved)}"))
    else:
        results.append(ValidationResult("template-check", True, "no unresolved placeholders found"))

    terraform_binary = shutil.which("terraform")
    if dry_run:
        results.append(ValidationResult("terraform-exec", True, "dry-run: would execute terraform fmt -check -recursive and terraform validate"))
        return results

    if terraform_binary is None:
        results.append(ValidationResult("terraform-exec", True, "terraform not installed, structural checks completed"))
        return results

    fmt = subprocess.run([terraform_binary, "fmt", "-check", "-recursive"], cwd=path, capture_output=True, text=True)
    results.append(ValidationResult("terraform fmt", fmt.returncode == 0, fmt.stdout.strip() or fmt.stderr.strip() or "terraform fmt passed"))

    init = subprocess.run([terraform_binary, "init", "-backend=false"], cwd=path, capture_output=True, text=True)
    if init.returncode != 0:
        results.append(ValidationResult("terraform init", False, init.stderr.strip() or "terraform init failed"))
        return results

    validate = subprocess.run([terraform_binary, "validate"], cwd=path, capture_output=True, text=True)
    results.append(ValidationResult("terraform validate", validate.returncode == 0, validate.stdout.strip() or validate.stderr.strip() or "terraform validate passed"))
    return results


def helm_lint_directory(path: str | Path, dry_run: bool = False) -> ValidationResult:
    path = Path(path)
    helm_binary = shutil.which("helm")
    if dry_run:
        return ValidationResult("helm-lint", True, f"dry-run: would execute helm lint {path}")
    if helm_binary is None:
        required = [(path / "Chart.yaml").exists(), (path / "values.yaml").exists(), (path / "templates").exists()]
        return ValidationResult("helm-lint", all(required), "helm not installed, checked chart structure only")

    proc = subprocess.run([helm_binary, "lint", str(path)], capture_output=True, text=True)
    return ValidationResult("helm-lint", proc.returncode == 0, proc.stdout.strip() or proc.stderr.strip() or "helm lint passed")
