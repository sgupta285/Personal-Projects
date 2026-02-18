"""
Options Pricing Analysis Toolkit
Generates vol surface plots, Greeks profiles, and MC convergence charts.

Usage: python analyze.py
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm
import os

plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["figure.dpi"] = 150

OUTPUT_DIR = "./charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Black-Scholes pricer (Python mirror) ---
def bs_price(S, K, T, r, sigma, q=0, option_type="call"):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


def bs_delta(S, K, T, r, sigma, q=0, option_type="call"):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    fwd = np.exp(-q * T)
    return fwd * norm.cdf(d1) if option_type == "call" else fwd * (norm.cdf(d1) - 1)


def bs_gamma(S, K, T, r, sigma, q=0):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))


def bs_vega(S, K, T, r, sigma, q=0):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100


def bs_theta(S, K, T, r, sigma, q=0, option_type="call"):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    t1 = -(S * np.exp(-q * T) * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == "call":
        return (t1 + q * S * np.exp(-q * T) * norm.cdf(d1) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    return (t1 - q * S * np.exp(-q * T) * norm.cdf(-d1) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365


# --- 1. Vol Surface 3D Plot ---
def plot_vol_surface():
    S, r = 100, 0.05
    strikes = np.linspace(70, 130, 30)
    expiries = np.linspace(0.05, 2.0, 20)
    K_grid, T_grid = np.meshgrid(strikes, expiries)

    base_vol, skew, smile = 0.20, -0.10, 0.05
    vol_grid = np.zeros_like(K_grid)
    for i in range(len(expiries)):
        for j in range(len(strikes)):
            m = np.log(strikes[j] / S)
            term_adj = np.sqrt(0.5 / expiries[i])
            vol_grid[i, j] = base_vol + skew * m * term_adj + smile * m**2
            vol_grid[i, j] = max(vol_grid[i, j], 0.05)

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(K_grid, T_grid, vol_grid * 100, cmap="coolwarm", alpha=0.85)
    ax.set_xlabel("Strike ($)")
    ax.set_ylabel("Expiry (years)")
    ax.set_zlabel("Implied Vol (%)")
    ax.set_title("Implied Volatility Surface", fontsize=14)
    fig.colorbar(surf, shrink=0.6, label="IV (%)")
    plt.savefig(f"{OUTPUT_DIR}/vol_surface_3d.png", bbox_inches="tight")
    plt.close()
    print(f"  Saved: {OUTPUT_DIR}/vol_surface_3d.png")


# --- 2. Greeks Profiles ---
def plot_greeks():
    K, T, r, sigma, q = 100, 1.0, 0.05, 0.20, 0.0
    spots = np.linspace(60, 140, 200)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Delta
    ax = axes[0, 0]
    ax.plot(spots, [bs_delta(s, K, T, r, sigma, q, "call") for s in spots], label="Call", color="#2196F3")
    ax.plot(spots, [bs_delta(s, K, T, r, sigma, q, "put") for s in spots], label="Put", color="#F44336")
    ax.axvline(K, linestyle="--", color="gray", alpha=0.5)
    ax.set_title("Delta")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Gamma
    ax = axes[0, 1]
    ax.plot(spots, [bs_gamma(s, K, T, r, sigma, q) for s in spots], color="#4CAF50")
    ax.axvline(K, linestyle="--", color="gray", alpha=0.5)
    ax.set_title("Gamma")
    ax.grid(True, alpha=0.3)

    # Vega
    ax = axes[1, 0]
    ax.plot(spots, [bs_vega(s, K, T, r, sigma, q) for s in spots], color="#FF9800")
    ax.axvline(K, linestyle="--", color="gray", alpha=0.5)
    ax.set_title("Vega (per 1% vol)")
    ax.set_xlabel("Spot Price ($)")
    ax.grid(True, alpha=0.3)

    # Theta
    ax = axes[1, 1]
    ax.plot(spots, [bs_theta(s, K, T, r, sigma, q, "call") for s in spots], label="Call", color="#2196F3")
    ax.plot(spots, [bs_theta(s, K, T, r, sigma, q, "put") for s in spots], label="Put", color="#F44336")
    ax.axvline(K, linestyle="--", color="gray", alpha=0.5)
    ax.set_title("Theta (per day)")
    ax.set_xlabel("Spot Price ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.suptitle(f"Greeks Profiles (K={K}, T={T}yr, σ={sigma*100}%)", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/greeks_profiles.png", bbox_inches="tight")
    plt.close()
    print(f"  Saved: {OUTPUT_DIR}/greeks_profiles.png")


# --- 3. MC Convergence ---
def plot_mc_convergence():
    S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
    bs = bs_price(S, K, T, r, sigma)

    path_counts = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    errors_std, errors_anti = [], []

    for n in path_counts:
        # Standard MC
        errs = []
        for seed in range(20):
            np.random.seed(seed)
            z = np.random.randn(n)
            ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
            payoffs = np.maximum(ST - K, 0)
            mc = np.exp(-r * T) * np.mean(payoffs)
            errs.append(abs(mc - bs))
        errors_std.append(np.mean(errs))

        # Antithetic MC
        errs = []
        for seed in range(20):
            np.random.seed(seed)
            z = np.random.randn(n // 2)
            z_all = np.concatenate([z, -z])
            ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z_all)
            payoffs = np.maximum(ST - K, 0)
            mc = np.exp(-r * T) * np.mean(payoffs)
            errs.append(abs(mc - bs))
        errors_anti.append(np.mean(errs))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.loglog(path_counts, errors_std, "o-", label="Standard MC", color="#F44336")
    ax.loglog(path_counts, errors_anti, "s-", label="Antithetic MC", color="#2196F3")
    ax.loglog(path_counts, [bs * 0.5 / np.sqrt(n) for n in path_counts],
              "--", color="gray", alpha=0.5, label="O(1/√N) reference")
    ax.set_xlabel("Number of Paths")
    ax.set_ylabel("Mean Absolute Error ($)")
    ax.set_title("Monte Carlo Convergence", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, which="both")
    plt.savefig(f"{OUTPUT_DIR}/mc_convergence.png", bbox_inches="tight")
    plt.close()
    print(f"  Saved: {OUTPUT_DIR}/mc_convergence.png")


# --- 4. Vol Smile at Different Expiries ---
def plot_vol_smile():
    S, r = 100, 0.05
    strikes = np.linspace(70, 130, 50)
    base_vol, skew, smile_param = 0.20, -0.10, 0.05

    fig, ax = plt.subplots(figsize=(12, 6))
    for T, color in [(0.1, "#F44336"), (0.25, "#FF9800"), (0.5, "#4CAF50"),
                      (1.0, "#2196F3"), (2.0, "#9C27B0")]:
        vols = []
        for K in strikes:
            m = np.log(K / S)
            adj = np.sqrt(0.5 / T)
            v = base_vol + skew * m * adj + smile_param * m**2
            vols.append(max(v, 0.05) * 100)
        ax.plot(strikes, vols, label=f"T={T}yr", color=color, linewidth=1.5)

    ax.axvline(S, linestyle="--", color="gray", alpha=0.4, label="ATM")
    ax.set_xlabel("Strike ($)")
    ax.set_ylabel("Implied Volatility (%)")
    ax.set_title("Volatility Smile by Expiry", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/vol_smile.png", bbox_inches="tight")
    plt.close()
    print(f"  Saved: {OUTPUT_DIR}/vol_smile.png")


if __name__ == "__main__":
    print("\nGenerating Options Pricing Charts...")
    plot_vol_surface()
    plot_greeks()
    plot_mc_convergence()
    plot_vol_smile()
    print(f"\nAll charts saved to: {OUTPUT_DIR}/\n")
