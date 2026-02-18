#pragma once

#include "pricing/types.h"
#include "utils/normal_dist.h"
#include <cmath>
#include <chrono>

namespace opt {

class BlackScholes {
public:
    static PricingResult price(const OptionParams& p) {
        auto t0 = std::chrono::high_resolution_clock::now();

        double d1 = calc_d1(p);
        double d2 = d1 - p.sigma * std::sqrt(p.T);

        double price;
        double df = std::exp(-p.r * p.T);
        double fwd_factor = std::exp(-p.q * p.T);

        if (p.type == OptionType::CALL) {
            price = p.S * fwd_factor * norm_cdf(d1) - p.K * df * norm_cdf(d2);
        } else {
            price = p.K * df * norm_cdf(-d2) - p.S * fwd_factor * norm_cdf(-d1);
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        return {price, 0.0, ms, "Black-Scholes", 0};
    }

    // --- Analytical Greeks (closed-form) ---
    static double delta(const OptionParams& p) {
        double d1 = calc_d1(p);
        double fwd = std::exp(-p.q * p.T);
        if (p.type == OptionType::CALL) return fwd * norm_cdf(d1);
        return fwd * (norm_cdf(d1) - 1.0);
    }

    static double gamma(const OptionParams& p) {
        double d1 = calc_d1(p);
        double fwd = std::exp(-p.q * p.T);
        return fwd * norm_pdf(d1) / (p.S * p.sigma * std::sqrt(p.T));
    }

    static double theta(const OptionParams& p) {
        double d1 = calc_d1(p);
        double d2 = d1 - p.sigma * std::sqrt(p.T);
        double fwd = std::exp(-p.q * p.T);
        double df = std::exp(-p.r * p.T);

        double term1 = -(p.S * fwd * norm_pdf(d1) * p.sigma) / (2.0 * std::sqrt(p.T));

        if (p.type == OptionType::CALL) {
            return (term1 + p.q * p.S * fwd * norm_cdf(d1) - p.r * p.K * df * norm_cdf(d2)) / 365.0;
        }
        return (term1 - p.q * p.S * fwd * norm_cdf(-d1) + p.r * p.K * df * norm_cdf(-d2)) / 365.0;
    }

    static double vega(const OptionParams& p) {
        double d1 = calc_d1(p);
        double fwd = std::exp(-p.q * p.T);
        return p.S * fwd * norm_pdf(d1) * std::sqrt(p.T) / 100.0; // Per 1% vol
    }

    static double rho(const OptionParams& p) {
        double d2 = calc_d1(p) - p.sigma * std::sqrt(p.T);
        double df = std::exp(-p.r * p.T);

        if (p.type == OptionType::CALL) {
            return p.K * p.T * df * norm_cdf(d2) / 100.0;
        }
        return -p.K * p.T * df * norm_cdf(-d2) / 100.0;
    }

    static double vanna(const OptionParams& p) {
        double d1 = calc_d1(p);
        double d2 = d1 - p.sigma * std::sqrt(p.T);
        double fwd = std::exp(-p.q * p.T);
        return -fwd * norm_pdf(d1) * d2 / p.sigma;
    }

    static double volga(const OptionParams& p) {
        double d1 = calc_d1(p);
        double d2 = d1 - p.sigma * std::sqrt(p.T);
        double fwd = std::exp(-p.q * p.T);
        return p.S * fwd * norm_pdf(d1) * std::sqrt(p.T) * d1 * d2 / p.sigma;
    }

    static Greeks all_greeks(const OptionParams& p) {
        auto t0 = std::chrono::high_resolution_clock::now();
        Greeks g;
        g.delta = delta(p);
        g.gamma = gamma(p);
        g.theta = theta(p);
        g.vega = vega(p);
        g.rho = rho(p);
        g.vanna = vanna(p);
        g.volga = volga(p);
        g.charm = 0.0; // Computed via FD
        g.speed = 0.0; // Computed via FD
        g.method = "BS-Analytical";
        auto t1 = std::chrono::high_resolution_clock::now();
        g.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
        return g;
    }

    // d1 helper
    static double calc_d1(const OptionParams& p) {
        return (std::log(p.S / p.K) + (p.r - p.q + 0.5 * p.sigma * p.sigma) * p.T) /
               (p.sigma * std::sqrt(p.T));
    }
};

} // namespace opt
