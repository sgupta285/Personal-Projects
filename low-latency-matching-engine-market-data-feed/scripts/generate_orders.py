from __future__ import annotations

import csv
import random
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "data" / "orders.csv"


def main() -> None:
    random.seed(42)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["action", "order_id", "side", "price", "quantity"])
        next_id = 1
        for _ in range(20000):
            if next_id % 17 == 0:
                writer.writerow(["CANCEL", random.randint(1, max(1, next_id - 1))])
                continue
            side = "B" if random.random() > 0.5 else "S"
            price = 10000 + random.randint(-40, 40)
            qty = random.randint(1, 200)
            writer.writerow(["ADD", next_id, side, price, qty])
            next_id += 1


if __name__ == "__main__":
    main()
