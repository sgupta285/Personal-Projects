"""
Trading Backtest Analysis Toolkit
Loads equity curves, trades, and metrics exported by the C++ engine
and generates publication-quality charts and performance reports.

Usage:
    python analyze.py --input ./output/momentum
    python analyze.py --input ./output/momentum --compare ./output/mean_reversion
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (14, 7)
plt.rcParams["figure.dpi"] = 150


def load_results(directory: str) -> dict:
    """Load all CSV results from a backtest output directory."""
    result = {"dir": directory}

    equity_path = os.path.join(directory, "equity_curve.csv")
    if os.path.exists(equity_path):
        df = pd.read_csv(equity_path)
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        result["equity"] = df

    trades_path = os.path.join(directory, "trades.csv")
    if os.path.exists(trades_path):
        result["trades"] = pd.read_csv(trades_path)

    metrics_path = os.path.join(directory, "metrics.csv")
    if os.path.exists(metrics_path):
        df = pd.read_csv(metrics_path)
        result["metrics"] = dict(zip(df["metric"], df["value"]))

    return result


def plot_equity_curve(results: dict, benchmark: pd.Series = None, output_dir: str = "."):
    """Plot equity curve with drawdown overlay."""
    df = results["equity"]
    strategy = results["metrics"].get("strategy", "Strategy")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), height_ratios=[3, 1],
                                     sharex=True, gridspec_kw={"hspace": 0.05})

    # Equity curve
    ax1.plot(df["date"], df["equity"], label=strategy, linewidth=1.5, color="#2196F3")

    if benchmark is not None:
        initial = df["equity"].iloc[0]
        bm_scaled = initial * (1 + benchmark).cumprod()
        ax1.plot(df["date"].iloc[:len(bm_scaled)], bm_scaled.values,
                 label="SPY (Buy & Hold)", linewidth=1.0, color="#999999", alpha=0.7)

    ax1.set_ylabel("Portfolio Value ($)")
    ax1.legend(loc="upper left")
    ax1.set_title(f"Equity Curve — {strategy}", fontsize=14)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax1.grid(True, alpha=0.3)

    # Drawdown
    ax2.fill_between(df["date"], df["drawdown"] * -100, 0,
                     alpha=0.4, color="#F44336", label="Drawdown")
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.legend(loc="lower left")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "equity_curve.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_monthly_returns(results: dict, output_dir: str = "."):
    """Plot monthly returns heatmap."""
    df = results["equity"]
    strategy = results["metrics"].get("strategy", "Strategy")

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # Compute monthly returns
    monthly = df.groupby(["year", "month"]).last()["equity"]
    monthly_ret = monthly.pct_change().reset_index()
    monthly_ret.columns = ["year", "month", "return"]
    monthly_ret = monthly_ret.dropna()

    pivot = monthly_ret.pivot(index="year", columns="month", values="return")
    pivot.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][:len(pivot.columns)]

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot * 100, annot=True, fmt=".1f", cmap="RdYlGn", center=0,
                ax=ax, cbar_kws={"label": "Return (%)"}, linewidths=0.5)
    ax.set_title(f"Monthly Returns (%) — {strategy}", fontsize=14)
    ax.set_ylabel("Year")

    path = os.path.join(output_dir, "monthly_returns.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_return_distribution(results: dict, output_dir: str = "."):
    """Plot daily return distribution with normal overlay."""
    df = results["equity"]
    strategy = results["metrics"].get("strategy", "Strategy")

    returns = df["daily_return"].dropna()
    returns = returns[returns != 0.0]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.hist(returns * 100, bins=100, density=True, alpha=0.7, color="#2196F3",
            label="Actual Distribution")

    # Normal overlay
    x = np.linspace(returns.min() * 100, returns.max() * 100, 200)
    ax.plot(x, stats.norm.pdf(x, returns.mean() * 100, returns.std() * 100),
            "r-", linewidth=2, label="Normal Distribution")

    skew = stats.skew(returns)
    kurt = stats.kurtosis(returns)
    ax.text(0.02, 0.95, f"Skew: {skew:.3f}\nExcess Kurt: {kurt:.3f}",
            transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    ax.set_xlabel("Daily Return (%)")
    ax.set_ylabel("Density")
    ax.set_title(f"Return Distribution — {strategy}", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    path = os.path.join(output_dir, "return_distribution.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_rolling_sharpe(results: dict, window: int = 126, output_dir: str = "."):
    """Plot rolling Sharpe ratio over time."""
    df = results["equity"]
    strategy = results["metrics"].get("strategy", "Strategy")

    returns = df["daily_return"]
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std()
    rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["date"], rolling_sharpe, linewidth=1.2, color="#2196F3")
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(y=1.0, color="green", linestyle="--", alpha=0.3, label="Sharpe = 1.0")
    ax.fill_between(df["date"], rolling_sharpe, 0,
                    where=(rolling_sharpe > 0), alpha=0.1, color="green")
    ax.fill_between(df["date"], rolling_sharpe, 0,
                    where=(rolling_sharpe < 0), alpha=0.1, color="red")

    ax.set_xlabel("Date")
    ax.set_ylabel(f"Rolling {window}-day Sharpe")
    ax.set_title(f"Rolling Sharpe Ratio — {strategy}", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    path = os.path.join(output_dir, "rolling_sharpe.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def print_performance_table(results: dict):
    """Print formatted performance metrics table."""
    m = results["metrics"]
    strategy = m.get("strategy", "Strategy")

    print(f"\n{'='*60}")
    print(f"  PERFORMANCE SUMMARY: {strategy}")
    print(f"{'='*60}")
    print(f"  Annualized Return:   {float(m.get('annualized_return', 0))*100:>8.1f}%")
    print(f"  Annualized Vol:      {float(m.get('annualized_volatility', 0))*100:>8.1f}%")
    print(f"  Sharpe Ratio:        {float(m.get('sharpe_ratio', 0)):>8.2f}")
    print(f"  Sortino Ratio:       {float(m.get('sortino_ratio', 0)):>8.2f}")
    print(f"  Calmar Ratio:        {float(m.get('calmar_ratio', 0)):>8.2f}")
    print(f"  Max Drawdown:        {float(m.get('max_drawdown', 0))*100:>8.1f}%")
    print(f"  Win Rate:            {float(m.get('win_rate', 0))*100:>8.1f}%")
    print(f"  Profit Factor:       {float(m.get('profit_factor', 0)):>8.2f}")
    print(f"  Alpha:               {float(m.get('alpha', 0))*100:>8.2f}%")
    print(f"  Beta:                {float(m.get('beta', 0)):>8.2f}")
    print(f"  Info Ratio:          {float(m.get('information_ratio', 0)):>8.2f}")
    print(f"  Total Trades:        {m.get('total_trades', 0):>8}")
    print(f"  VaR (95%):           {float(m.get('var_95', 0))*100:>8.2f}%")
    print(f"  CVaR (95%):          {float(m.get('cvar_95', 0))*100:>8.2f}%")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Trading Backtest Analysis")
    parser.add_argument("--input", "-i", required=True, help="Results directory")
    parser.add_argument("--compare", "-c", help="Second results directory for comparison")
    parser.add_argument("--output", "-o", help="Output directory for charts (default: same as input)")
    args = parser.parse_args()

    output_dir = args.output or args.input
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nLoading results from: {args.input}")
    results = load_results(args.input)

    if "equity" not in results:
        print("ERROR: No equity_curve.csv found")
        sys.exit(1)

    print_performance_table(results)

    print("Generating charts...")
    plot_equity_curve(results, output_dir=output_dir)
    plot_monthly_returns(results, output_dir=output_dir)
    plot_return_distribution(results, output_dir=output_dir)
    plot_rolling_sharpe(results, output_dir=output_dir)

    print(f"\nAll charts saved to: {output_dir}/")


if __name__ == "__main__":
    main()
