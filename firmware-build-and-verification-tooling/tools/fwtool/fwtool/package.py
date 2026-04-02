from __future__ import annotations

import io
import json
import tarfile
import time
from pathlib import Path

from .build import REPO_ROOT, build
from .utils import ensure_dir, sha256_file, stable_json_dumps

FIXED_MTIME = 1_700_000_000


def _add_file(tar: tarfile.TarFile, arcname: str, data: bytes, mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name=arcname)
    info.size = len(data)
    info.mtime = FIXED_MTIME
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    tar.addfile(info, io.BytesIO(data))


def create_release(board: str = "demo-board", version: str = "0.1.0") -> Path:
    result = build(board=board, version=version)
    dist_dir = ensure_dir(REPO_ROOT / "dist")
    release_name = f"firmware-{board}-{version}"
    tar_path = dist_dir / f"{release_name}.tar.gz"

    manifest = json.loads(result.manifest_path.read_text())
    verification = {
        "created_at_epoch": FIXED_MTIME,
        "release_name": release_name,
        "board": board,
        "version": version,
        "build_cache_hit": result.cache_hit,
        "artifacts": manifest["artifacts"],
    }

    with tarfile.open(tar_path, mode="w:gz", format=tarfile.PAX_FORMAT, compresslevel=9) as tar:
        _add_file(tar, f"{release_name}/manifest.json", stable_json_dumps(manifest).encode())
        _add_file(tar, f"{release_name}/verification.json", stable_json_dumps(verification).encode())
        for artifact in manifest["artifacts"]:
            binary_path = REPO_ROOT / artifact["binary"]
            _add_file(tar, f"{release_name}/{Path(artifact['binary']).name}", binary_path.read_bytes())
        notes = (
            "Deterministic firmware release bundle\n"
            f"Board: {board}\n"
            f"Version: {version}\n"
            "Contents: manifest, verification payload, raw binary images\n"
        )
        _add_file(tar, f"{release_name}/RELEASE_NOTES.txt", notes.encode())

    checksum_path = dist_dir / f"{release_name}.sha256"
    checksum_path.write_text(f"{sha256_file(tar_path)}  {tar_path.name}\n")
    return tar_path
