from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd



def write_summary_json(summary: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(summary, indent=2))



def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)



def plot_equity_curve(equity_curve: pd.Series, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4.5))
    equity_curve.plot()
    plt.title("Walk-Forward Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio value")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
