/**
 * Performance benchmark: BS vs MC vs Binomial, SIMD impact, variance reduction comparison.
 */

#include "pricing/black_scholes.h"
#include "pricing/binomial_tree.h"
#include "monte_carlo/mc_engine.h"
#include "greeks/finite_difference.h"
#include "calibration/vol_surface.h"
#include "utils/timer.h"

#include <iostream>
#include <iomanip>
#include <vector>

using namespace opt;

int main() {
    std::cout << std::string(60, '=') << "\n";
    std::cout << "  OPTIONS ENGINE BENCHMARK\n";
    std::cout << std::string(60, '=') << "\n\n";

    #ifdef _OPENMP
    std::cout << "OpenMP: ENABLED\n";
    #endif
    #ifdef USE_AVX2
    std::cout << "SIMD: AVX2\n";
    #elif defined(USE_SSE42)
    std::cout << "SIMD: SSE4.2\n";
    #endif

    OptionParams call{100.0, 100.0, 1.0, 0.05, 0.20, 0.02, OptionType::CALL};
    int iterations = 10000;

    // --- Black-Scholes throughput ---
    {
        Timer t("BS x " + std::to_string(iterations));
        double sum = 0;
        for (int i = 0; i < iterations; ++i) {
            sum += BlackScholes::price(call).price;
        }
        std::cout << "  Avg price: " << std::fixed << std::setprecision(4) << sum / iterations << "\n";
    }

    // --- Monte Carlo scaling ---
    std::cout << "\nMonte Carlo scaling (Antithetic):\n";
    for (int paths : {1000, 5000, 10000, 50000, 100000}) {
        auto result = MonteCarloEngine::price(call, paths, VarianceReduction::ANTITHETIC);
        double err = std::abs(result.price - BlackScholes::price(call).price);
        std::cout << "  " << std::setw(7) << paths << " paths: $" << std::setprecision(4) << result.price
                  << "  SE=$" << result.std_error
                  << "  Err=$" << std::setprecision(6) << err
                  << "  " << std::setprecision(1) << result.elapsed_ms << " ms\n";
    }

    // --- Variance reduction comparison ---
    std::cout << "\nVariance Reduction (10K paths, 100 trials):\n";
    struct VRTest { VarianceReduction vr; std::string name; };
    std::vector<VRTest> tests = {
        {VarianceReduction::NONE, "Standard"},
        {VarianceReduction::ANTITHETIC, "Antithetic"},
        {VarianceReduction::STRATIFIED, "Stratified"},
        {VarianceReduction::CONTROL_VARIATE, "Control Variate"},
    };

    double bs_price = BlackScholes::price(call).price;
    for (const auto& test : tests) {
        double total_se = 0, total_err = 0, total_ms = 0;
        for (int trial = 0; trial < 100; ++trial) {
            auto r = MonteCarloEngine::price(call, 10000, test.vr, 42 + trial);
            total_se += r.std_error;
            total_err += std::abs(r.price - bs_price);
            total_ms += r.elapsed_ms;
        }
        std::cout << "  " << std::setw(16) << std::left << test.name
                  << " Avg SE=$" << std::fixed << std::setprecision(4) << total_se / 100
                  << "  Avg Err=$" << total_err / 100
                  << "  Avg " << std::setprecision(1) << total_ms / 100 << " ms\n";
    }

    // --- Binomial tree convergence ---
    std::cout << "\nBinomial Tree convergence:\n";
    for (int steps : {50, 100, 200, 500, 1000, 2000}) {
        auto r = BinomialTree::price(call, steps);
        double err = std::abs(r.price - bs_price);
        std::cout << "  " << std::setw(5) << steps << " steps: $" << std::setprecision(6) << r.price
                  << "  Err=$" << err << "  " << std::setprecision(1) << r.elapsed_ms << " ms\n";
    }

    // --- Greeks throughput ---
    std::cout << "\nGreeks throughput (10K iterations):\n";
    {
        Timer t("Analytical Greeks x 10000");
        for (int i = 0; i < 10000; ++i) BlackScholes::all_greeks(call);
    }
    {
        Timer t("FD Greeks x 10000");
        for (int i = 0; i < 10000; ++i) FiniteDifferenceGreeks::compute(call);
    }

    // --- Vol surface calibration ---
    std::cout << "\nVol Surface Calibration (9x5 = 45 points):\n";
    {
        std::vector<double> strikes = {80, 85, 90, 95, 100, 105, 110, 115, 120};
        std::vector<double> expiries = {0.08, 0.25, 0.50, 1.00, 2.00};
        auto quotes = VolSurface::generate_market_quotes(100.0, 0.05, strikes, expiries);
        Timer t("Calibration");
        auto result = VolSurface::calibrate(quotes, 100.0, 0.05);
        std::cout << "  RMSE: " << std::scientific << result.total_rmse << "\n";
    }

    std::cout << "\n" << std::string(60, '=') << "\n";
    return 0;
}
