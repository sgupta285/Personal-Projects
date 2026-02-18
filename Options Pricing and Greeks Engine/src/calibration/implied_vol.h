#pragma once

#include "pricing/types.h"
#include "pricing/black_scholes.h"
#include <cmath>
#include <stdexcept>
#include <algorithm>

namespace opt {

class ImpliedVolSolver {
public:
    // Newton-Raphson implied volatility solver
    static double solve(
        double market_price,
        double S, double K, double T, double r, double q,
        OptionType type,
        double tol = 1e-8,
        int max_iter = 100
    ) {
        // Initial guess using Brenner-Subrahmanyam approximation
        double sigma = std::sqrt(2.0 * M_PI / T) * market_price / S;
        sigma = std::clamp(sigma, 0.01, 5.0);

        for (int i = 0; i < max_iter; ++i) {
            OptionParams p{S, K, T, r, sigma, q, type};
            double model_price = BlackScholes::price(p).price;
            double vega = BlackScholes::vega(p) * 100.0; // Convert from per-1% to per-unit

            double diff = model_price - market_price;

            if (std::abs(diff) < tol) return sigma;
            if (std::abs(vega) < 1e-12) break; // Vega too small

            // Newton step with damping
            double step = diff / vega;
            sigma -= step;

            // Bound sigma
            sigma = std::clamp(sigma, 0.001, 10.0);
        }

        // Fallback: bisection if Newton fails
        return bisection_solve(market_price, S, K, T, r, q, type, tol);
    }

    // Bisection fallback (more robust, slower)
    static double bisection_solve(
        double market_price,
        double S, double K, double T, double r, double q,
        OptionType type,
        double tol = 1e-6
    ) {
        double lo = 0.001, hi = 5.0;

        for (int i = 0; i < 200; ++i) {
            double mid = (lo + hi) / 2.0;
            OptionParams p{S, K, T, r, mid, q, type};
            double model_price = BlackScholes::price(p).price;

            if (std::abs(model_price - market_price) < tol) return mid;

            if (model_price > market_price) {
                hi = mid;
            } else {
                lo = mid;
            }
        }

        return (lo + hi) / 2.0; // Best estimate
    }
};

} // namespace opt
