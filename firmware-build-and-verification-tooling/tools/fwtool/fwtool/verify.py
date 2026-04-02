from __future__ import annotations

import json
import socket
import tarfile
from pathlib import Path
from typing import Any

from .build import REPO_ROOT
from .package import create_release
from .utils import sha256_file


def verify_release(release_path: Path) -> dict[str, Any]:
    with tarfile.open(release_path, mode="r:gz") as tar:
        members = tar.getnames()
        manifest_name = next(name for name in members if name.endswith("manifest.json"))
        verification_name = next(name for name in members if name.endswith("verification.json"))
        manifest = json.load(tar.extractfile(manifest_name))
        verification = json.load(tar.extractfile(verification_name))
        checks = []
        for artifact in manifest["artifacts"]:
            member_name = next(name for name in members if name.endswith(Path(artifact["binary"]).name))
            member = tar.extractfile(member_name).read()
            actual = sha256_bytes(member)
            checks.append(
                {
                    "component": artifact["component"],
                    "expected_sha256": artifact["sha256"],
                    "actual_sha256": actual,
                    "size_bytes": len(member),
                    "sha_match": actual == artifact["sha256"],
                }
            )
        return {
            "board": verification["board"],
            "version": verification["version"],
            "checks": checks,
            "all_passed": all(item["sha_match"] for item in checks),
        }


def sha256_bytes(data: bytes) -> str:
    import hashlib

    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def verify_device_handshake(host: str, port: int, board: str, verification: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"board": board, "verification": verification}).encode() + b"\n"
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(payload)
        response = sock.recv(4096)
    return json.loads(response.decode())
