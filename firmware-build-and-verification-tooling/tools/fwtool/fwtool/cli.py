from __future__ import annotations

import argparse
import json
from pathlib import Path

from .build import build, clean
from .device_sim import start
from .package import create_release
from .verify import verify_device_handshake, verify_release


def cmd_build(args: argparse.Namespace) -> int:
    result = build(board=args.board, version=args.version, config_file=args.config)
    print(json.dumps({
        "board": result.board,
        "version": result.version,
        "manifest": str(result.manifest_path),
        "cache_hit": result.cache_hit,
    }, indent=2))
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    path = create_release(board=args.board, version=args.version)
    print(json.dumps({"release": str(path)}, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    result = verify_release(Path(args.release))
    print(json.dumps(result, indent=2))
    return 0 if result["all_passed"] else 1


def cmd_hil(args: argparse.Namespace) -> int:
    handle = start(host=args.host, port=args.port)
    try:
        release_path = create_release(board=args.board, version=args.version)
        verification = verify_release(release_path)
        response = verify_device_handshake(args.host, args.port, args.board, verification)
        print(json.dumps(response, indent=2))
        return 0 if response.get("ok") else 1
    finally:
        handle.stop()


def cmd_clean(args: argparse.Namespace) -> int:
    clean()
    print("cleaned")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fwtool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("--board", default="demo-board")
    p_build.add_argument("--version", default="0.1.0")
    p_build.add_argument("--config", default="config/demo_board.json")
    p_build.set_defaults(func=cmd_build)

    p_package = sub.add_parser("package")
    p_package.add_argument("--board", default="demo-board")
    p_package.add_argument("--version", default="0.1.0")
    p_package.set_defaults(func=cmd_package)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("release")
    p_verify.set_defaults(func=cmd_verify)

    p_hil = sub.add_parser("hil")
    p_hil.add_argument("--board", default="demo-board")
    p_hil.add_argument("--version", default="0.1.0")
    p_hil.add_argument("--host", default="127.0.0.1")
    p_hil.add_argument("--port", type=int, default=9107)
    p_hil.set_defaults(func=cmd_hil)

    p_clean = sub.add_parser("clean")
    p_clean.set_defaults(func=cmd_clean)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
