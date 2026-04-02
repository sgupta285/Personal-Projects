from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**dict(), **__import__("os").environ}
    env["PYTHONPATH"] = str(REPO_ROOT / "tools" / "fwtool")
    return subprocess.run(
        [sys.executable, "-m", "fwtool.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def test_build_manifest_exists() -> None:
    result = run_cli("build", "--version", "1.2.3")
    payload = json.loads(result.stdout)
    assert payload["version"] == "1.2.3"
    assert Path(payload["manifest"]).exists()


def test_package_and_verify() -> None:
    release = json.loads(run_cli("package", "--version", "1.2.4").stdout)["release"]
    verification = json.loads(run_cli("verify", release).stdout)
    assert verification["all_passed"] is True


def test_hil_round_trip() -> None:
    response = json.loads(run_cli("hil", "--version", "1.2.5", "--port", "9110").stdout)
    assert response["ok"] is True
