/**
 * Benchmark: measures simulation throughput and OpenMP scaling.
 * Target: 100K+ simulations at 3x+ speedup with OpenMP.
 */

#include "engine/backtest_engine.h"
#include "data/data_generator.h"
#include "strategies/momentum.h"
#include <iostream>
#include <chrono>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

int main() {
    std::cout << std::string(60, '=') << "\n";
    std::cout << "PERFORMANCE BENCHMARK\n";
    std::cout << std::string(60, '=') << "\n\n";

    #ifdef _OPENMP
    std::cout << "OpenMP: ENABLED (" << omp_get_max_threads() << " threads)\n";
    #else
    std::cout << "OpenMP: DISABLED (single-threaded)\n";
    #endif

    #ifdef USE_AVX2
    std::cout << "SIMD: AVX2 enabled\n";
    #elif defined(USE_SSE42)
    std::cout << "SIMD: SSE4.2 enabled\n";
    #else
    std::cout << "SIMD: None\n";
    #endif

    // Small universe for throughput testing
    int num_symbols = 10;
    int num_days = 504; // 2 years
    int num_sims = 1000;

    std::cout << "\nConfig: " << num_symbols << " symbols x " << num_days
              << " days x " << num_sims << " simulations\n\n";

    auto data = bt::DataGenerator::generate_universe(num_symbols, num_days);

    bt::BacktestConfig config;
    config.initial_capital = 1'000'000.0;
    config.volatility_sizing = true;
    config.max_drawdown_pct = 0.50;

    // --- Single-threaded benchmark ---
    {
        auto t0 = std::chrono::high_resolution_clock::now();

        double total_sharpe = 0.0;
        for (int i = 0; i < num_sims; ++i) {
            auto strategy = std::make_shared<bt::MomentumStrategy>(252, 21, 10, 21);
            bt::BacktestEngine engine(config, strategy, data);
            auto metrics = engine.run();
            total_sharpe += metrics.sharpe_ratio;
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double>(t1 - t0).count();

        std::cout << "Single-threaded: " << std::fixed << std::setprecision(2) << elapsed << "s"
                  << " (" << std::setprecision(0) << num_sims / elapsed << " sims/sec)"
                  << " avg Sharpe: " << std::setprecision(3) << total_sharpe / num_sims << "\n";
    }

    // --- Multi-threaded benchmark (OpenMP) ---
    {
        auto t0 = std::chrono::high_resolution_clock::now();

        double total_sharpe = 0.0;
        #pragma omp parallel for reduction(+:total_sharpe) schedule(dynamic, 10)
        for (int i = 0; i < num_sims; ++i) {
            auto strategy = std::make_shared<bt::MomentumStrategy>(252, 21, 10, 21);
            bt::BacktestEngine engine(config, strategy, data);
            auto metrics = engine.run();
            total_sharpe += metrics.sharpe_ratio;
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double>(t1 - t0).count();

        std::cout << "Multi-threaded:  " << std::fixed << std::setprecision(2) << elapsed << "s"
                  << " (" << std::setprecision(0) << num_sims / elapsed << " sims/sec)"
                  << " avg Sharpe: " << std::setprecision(3) << total_sharpe / num_sims << "\n";
    }

    std::cout << "\n" << std::string(60, '=') << "\n";
    return 0;
}
