#pragma once

#include "pricing/types.h"
#include "utils/random_gen.h"
#include <cmath>
#include <chrono>
#include <numeric>
#include <algorithm>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace opt {

enum class VarianceReduction { NONE, ANTITHETIC, STRATIFIED, CONTROL_VARIATE };

class MonteCarloEngine {
public:
    static PricingResult price(
        const OptionParams& p,
        int num_paths = 10000,
        VarianceReduction vr = VarianceReduction::ANTITHETIC,
        unsigned seed = 42
    ) {
        auto t0 = std::chrono::high_resolution_clock::now();

        std::vector<double> payoffs(num_paths);
        double dt = p.T;
        double drift = (p.r - p.q - 0.5 * p.sigma * p.sigma) * dt;
        double vol_sqrt_dt = p.sigma * std::sqrt(dt);
        double df = std::exp(-p.r * p.T);

        // Generate random numbers based on variance reduction method
        std::vector<double> z;
        switch (vr) {
            case VarianceReduction::ANTITHETIC:
                z = RandomGenerator::generate_antithetic(num_paths, seed);
                break;
            case VarianceReduction::STRATIFIED:
                z = RandomGenerator::generate_stratified(num_paths, seed);
                break;
            default:
                z = RandomGenerator::generate_normals(num_paths, seed);
                break;
        }

        // Simulate paths (parallelized)
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < num_paths; ++i) {
            double ST = p.S * std::exp(drift + vol_sqrt_dt * z[i]);
            payoffs[i] = intrinsic_value(ST, p.K, p.type);
        }

        // Control variate adjustment
        double price_est;
        double std_err;

        if (vr == VarianceReduction::CONTROL_VARIATE) {
            // Use forward price as control variate
            double fwd = p.S * std::exp((p.r - p.q) * p.T);
            std::vector<double> terminals(num_paths);

            #pragma omp parallel for schedule(static)
            for (int i = 0; i < num_paths; ++i) {
                terminals[i] = p.S * std::exp(drift + vol_sqrt_dt * z[i]);
            }

            double mean_terminal = std::accumulate(terminals.begin(), terminals.end(), 0.0) / num_paths;
            double mean_payoff = std::accumulate(payoffs.begin(), payoffs.end(), 0.0) / num_paths;

            // Compute covariance and beta
            double cov = 0.0, var_control = 0.0;
            for (int i = 0; i < num_paths; ++i) {
                double dc = terminals[i] - mean_terminal;
                double dp = payoffs[i] - mean_payoff;
                cov += dc * dp;
                var_control += dc * dc;
            }
            double beta = (var_control > 0.0) ? cov / var_control : 0.0;

            // Adjusted payoffs
            std::vector<double> adjusted(num_paths);
            for (int i = 0; i < num_paths; ++i) {
                adjusted[i] = payoffs[i] - beta * (terminals[i] - fwd);
            }

            double sum = std::accumulate(adjusted.begin(), adjusted.end(), 0.0);
            price_est = df * sum / num_paths;

            double var = 0.0;
            double adj_mean = sum / num_paths;
            for (double a : adjusted) var += (a - adj_mean) * (a - adj_mean);
            var /= (num_paths - 1);
            std_err = df * std::sqrt(var / num_paths);
        } else {
            double sum = std::accumulate(payoffs.begin(), payoffs.end(), 0.0);
            double mean = sum / num_paths;
            price_est = df * mean;

            double var = 0.0;
            for (double pay : payoffs) var += (pay - mean) * (pay - mean);
            var /= (num_paths - 1);
            std_err = df * std::sqrt(var / num_paths);
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        std::string method = "Monte Carlo";
        switch (vr) {
            case VarianceReduction::ANTITHETIC: method += " (Antithetic)"; break;
            case VarianceReduction::STRATIFIED: method += " (Stratified)"; break;
            case VarianceReduction::CONTROL_VARIATE: method += " (Control Variate)"; break;
            default: break;
        }

        return {std::max(price_est, 0.0), std_err, ms, method, num_paths};
    }

    // Multi-step path simulation for path-dependent options
    static PricingResult price_multistep(
        const OptionParams& p,
        int num_paths = 10000,
        int num_steps = 252,
        unsigned seed = 42
    ) {
        auto t0 = std::chrono::high_resolution_clock::now();

        double dt = p.T / num_steps;
        double drift = (p.r - p.q - 0.5 * p.sigma * p.sigma) * dt;
        double vol_sqrt_dt = p.sigma * std::sqrt(dt);
        double df = std::exp(-p.r * p.T);

        std::vector<double> payoffs(num_paths);

        #pragma omp parallel
        {
            unsigned thread_seed = seed + omp_get_thread_num() * 1000;
            std::mt19937_64 rng(thread_seed);
            std::normal_distribution<double> norm(0.0, 1.0);

            #pragma omp for schedule(static)
            for (int i = 0; i < num_paths; ++i) {
                double S = p.S;
                for (int t = 0; t < num_steps; ++t) {
                    double z = norm(rng);
                    S *= std::exp(drift + vol_sqrt_dt * z);
                }
                payoffs[i] = intrinsic_value(S, p.K, p.type);
            }
        }

        double sum = std::accumulate(payoffs.begin(), payoffs.end(), 0.0);
        double mean = sum / num_paths;
        double price_est = df * mean;

        double var = 0.0;
        for (double pay : payoffs) var += (pay - mean) * (pay - mean);
        var /= (num_paths - 1);
        double std_err = df * std::sqrt(var / num_paths);

        auto t1 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        return {std::max(price_est, 0.0), std_err, ms,
                "MC MultiStep (" + std::to_string(num_steps) + " steps)", num_paths};
    }
};

} // namespace opt
