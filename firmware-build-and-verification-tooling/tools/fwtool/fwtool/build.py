from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import ensure_dir, sha256_file, stable_json_dumps

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class BuildResult:
    board: str
    version: str
    build_dir: Path
    cache_hit: bool
    manifest_path: Path


def _load_config(config_path: Path) -> dict[str, Any]:
    return json.loads(config_path.read_text())


def _build_fingerprint(config: dict[str, Any], version: str) -> str:
    digest = hashlib.sha256()
    digest.update(version.encode())
    digest.update(stable_json_dumps(config).encode())
    for path in sorted((REPO_ROOT / "src").rglob("*.c")):
        digest.update(path.read_bytes())
    for path in sorted((REPO_ROOT / "include").rglob("*.h")):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_make(board: str, version: str) -> None:
    env = os.environ.copy()
    subprocess.run(
        ["make", f"BOARD={board}", f"VERSION={version}"],
        cwd=REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def build(board: str = "demo-board", version: str = "0.1.0", config_file: str = "config/demo_board.json") -> BuildResult:
    config_path = REPO_ROOT / config_file
    config = _load_config(config_path)
    build_dir = REPO_ROOT / "build" / board
    cache_dir = ensure_dir(REPO_ROOT / ".cache" / board)
    cache_index = cache_dir / "build_index.json"
    fingerprint = _build_fingerprint(config, version)
    cache_payload = json.loads(cache_index.read_text()) if cache_index.exists() else {}
    cache_hit = cache_payload.get("fingerprint") == fingerprint and (build_dir / "bin" / "app.bin").exists()

    if not cache_hit:
        run_make(board=board, version=version)
        cache_index.write_text(stable_json_dumps({"fingerprint": fingerprint, "version": version}))

    artifacts: list[dict[str, Any]] = []
    for component in config["components"]:
        stem = "app" if component == "application" else component
        bin_path = build_dir / "bin" / f"{stem}.bin"
        elf_path = build_dir / "bin" / f"{stem}.elf"
        if not bin_path.exists():
            raise FileNotFoundError(bin_path)
        artifacts.append(
            {
                "component": component,
                "binary": str(bin_path.relative_to(REPO_ROOT)),
                "elf": str(elf_path.relative_to(REPO_ROOT)),
                "sha256": sha256_file(bin_path),
                "size_bytes": bin_path.stat().st_size,
            }
        )

    manifest = {
        "board": board,
        "version": version,
        "config": str(config_path.relative_to(REPO_ROOT)),
        "cache_hit": cache_hit,
        "artifacts": artifacts,
    }
    manifest_path = build_dir / "manifest.json"
    ensure_dir(manifest_path.parent)
    manifest_path.write_text(stable_json_dumps(manifest))
    return BuildResult(board=board, version=version, build_dir=build_dir, cache_hit=cache_hit, manifest_path=manifest_path)


def clean() -> None:
    for target in [REPO_ROOT / "build", REPO_ROOT / "dist"]:
        if target.exists():
            shutil.rmtree(target)
