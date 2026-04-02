from __future__ import annotations

import hashlib
import json
import socketserver
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .build import REPO_ROOT


@dataclass
class SimulatorHandle:
    server: socketserver.TCPServer
    thread: threading.Thread
    host: str
    port: int

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class DeviceRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline().decode().strip()
        if not line:
            return
        payload = json.loads(line)
        board = payload.get("board", "unknown")
        verification = payload.get("verification", {})
        digest = hashlib.sha256(json.dumps(verification, sort_keys=True).encode()).hexdigest()
        response = {"ok": True, "board": board, "session_digest": digest}
        self.wfile.write((json.dumps(response) + "\n").encode())


def start(host: str = "127.0.0.1", port: int = 9107) -> SimulatorHandle:
    server = socketserver.TCPServer((host, port), DeviceRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return SimulatorHandle(server=server, thread=thread, host=host, port=port)
