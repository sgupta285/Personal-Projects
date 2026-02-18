# 📊 Options Pricing & Greeks Engine

C++ options pricing and risk engine supporting Black-Scholes analytical pricing, Monte Carlo simulation (10K+ paths) with variance reduction, Greeks via both closed-form and finite differences, implied volatility via Newton-Raphson, and volatility surface calibration.

99.8% accuracy vs analytical benchmarks, Greeks <0.1% error, <2s runtimes with SIMD + variance reduction optimization.

---

## Features

- **Black-Scholes** — closed-form European call/put pricing with dividend yield
- **Monte Carlo** — 4 variance reduction methods: standard, antithetic, stratified, control variate
- **Binomial Tree** — Cox-Ross-Rubinstein for American options (early exercise)
- **Analytical Greeks** — Delta, Gamma, Theta, Vega, Rho, Vanna, Volga (closed-form)
- **Finite Difference Greeks** — Central differences for all Greeks including Charm and Speed (3rd-order)
- **Implied Volatility** — Newton-Raphson with Brenner-Subrahmanyam initial guess and bisection fallback
- **Vol Surface Calibration** — Parallel calibration of strike×expiry grid with SVI-like smile parameterization
- **SIMD Vectorization** — AVX2 vectorized normal CDF for batch pricing
- **OpenMP Parallelization** — Parallel MC paths and vol surface calibration
- **Python Visualization** — 3D vol surface, Greeks profiles, MC convergence, vol smile charts

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    PRICING LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Black-Scholes│  │ Monte Carlo  │  │ Binomial     │   │
│  │ (Analytical) │  │ (10K+ paths) │  │ Tree (CRR)   │   │
│  │              │  │ + Variance   │  │ + American   │   │
│  │              │  │   Reduction  │  │   Exercise   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         └─────────────────┼─────────────────┘            │
│                           ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │                   GREEKS LAYER                      │  │
│  │  ┌──────────────────┐  ┌────────────────────────┐  │  │
│  │  │ Analytical       │  │ Finite Difference      │  │  │
│  │  │ Δ Γ Θ ν ρ vanna │  │ Δ Γ Θ ν ρ vanna volga│  │  │
│  │  │ volga            │  │ charm speed            │  │  │
│  │  └──────────────────┘  └────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                           ▼                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │               CALIBRATION LAYER                     │  │
│  │  ┌──────────────────┐  ┌────────────────────────┐  │  │
│  │  │ Implied Vol      │  │ Vol Surface            │  │  │
│  │  │ Newton-Raphson   │  │ Strike × Expiry grid   │  │  │
│  │  │ + Bisection      │  │ Parallel calibration   │  │  │
│  │  └──────────────────┘  └────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Build
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# Run pricer (full demo: pricing, Greeks, IV, vol surface)
./build/options_pricer

# Custom parameters
./build/options_pricer --spot 150 --strike 145 --vol 0.25 --mc-paths 50000

# Run benchmark
./build/benchmark

# Run tests
cd build && ctest --output-on-failure

# Python charts
cd python && pip install -r requirements.txt
python analysis/analyze.py
```

## Performance

| Method | Accuracy | Runtime |
|--------|----------|---------|
| Black-Scholes | Exact (reference) | <0.01 ms |
| Monte Carlo (10K, Antithetic) | 99.8% vs BS | ~2 ms |
| Monte Carlo (100K, Control Var) | 99.95% vs BS | ~15 ms |
| Binomial Tree (1000 steps) | 99.99% vs BS | ~5 ms |
| Greeks (Analytical vs FD) | <0.1% error | <0.1 ms |
| Implied Vol (Newton-Raphson) | <1e-8 error | <0.01 ms |
| Vol Surface (45 points) | RMSE <0.001 | ~5 ms |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Engine | C++20, CMake |
| Parallelism | OpenMP |
| Vectorization | AVX2/SSE4.2 |
| Visualization | Python, matplotlib, scipy |
| CI | GitHub Actions |

## License

MIT
