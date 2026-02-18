"""
Visualization: equity curves, spread z-scores, pair scatter plots.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 150


def plot_equity_curve(snapshots, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    dates = [s.timestamp for s in snapshots]
    equity = [s.equity for s in snapshots]
    dd = [s.drawdown for s in snapshots]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1], sharex=True)
    ax1.plot(dates, equity, color="#2196F3", linewidth=1.2)
    ax1.set_ylabel("Portfolio Equity ($)")
    ax1.set_title("Pairs Trading — Equity Curve")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(dates, [-d * 100 for d in dd], 0, alpha=0.4, color="#F44336")
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/equity_curve.png", bbox_inches="tight")
    plt.close()


def plot_spread_zscore(prices_a, prices_b, hedge_ratio, window=60, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    spread = prices_a - hedge_ratio * prices_b
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    z = (spread - mean) / std

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    ax1.plot(spread.index, spread, color="#2196F3", linewidth=0.8)
    ax1.plot(spread.index, mean, color="orange", linewidth=1)
    ax1.fill_between(spread.index, mean - 2 * std, mean + 2 * std, alpha=0.15, color="orange")
    ax1.set_ylabel("Spread")
    ax1.set_title("Pair Spread & Z-Score")
    ax1.grid(True, alpha=0.3)

    ax2.plot(z.index, z, color="#4CAF50", linewidth=0.8)
    ax2.axhline(2, linestyle="--", color="red", alpha=0.5, label="Entry ±2σ")
    ax2.axhline(-2, linestyle="--", color="red", alpha=0.5)
    ax2.axhline(0, linestyle="-", color="gray", alpha=0.3)
    ax2.set_ylabel("Z-Score")
    ax2.set_xlabel("Date")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/spread_zscore.png", bbox_inches="tight")
    plt.close()


def plot_trade_distribution(trades, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    if not trades:
        return

    pnls = [t.pnl for t in trades]
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#4CAF50" if p > 0 else "#F44336" for p in pnls]
    ax.bar(range(len(pnls)), pnls, color=colors, width=0.8)
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Trade #")
    ax.set_ylabel("P&L ($)")
    ax.set_title("Trade P&L Distribution")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/trade_pnl.png", bbox_inches="tight")
    plt.close()
