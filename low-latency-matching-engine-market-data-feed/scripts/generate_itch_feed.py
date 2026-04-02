from __future__ import annotations

from pathlib import Path
import struct

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "itch_feed.bin"


def encode_add(order_id: int, side: bytes, price: int, qty: int) -> bytes:
    return struct.pack("<cQcqq", b"A", order_id, side, price, qty)


def encode_cancel(order_id: int) -> bytes:
    return struct.pack("<cQ", b"C", order_id)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = b"".join(
        [
            encode_add(1, b"B", 10000, 50),
            encode_add(2, b"S", 10100, 40),
            encode_add(3, b"B", 10100, 25),
            encode_cancel(1),
        ]
    )
    OUTPUT.write_bytes(payload)


if __name__ == "__main__":
    main()
