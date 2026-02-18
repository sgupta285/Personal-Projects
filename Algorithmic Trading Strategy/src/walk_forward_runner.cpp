/**
 * Walk-Forward Validation Runner
 * Runs the momentum strategy across rolling train/test windows
 * to validate out-of-sample performance and detect overfitting.
 */

#include "engine/backtest_engine.h"
#include "data/data_generator.h"
#include "strategies/momentum.h"
#include "utils/walk_forward.h"

#include <iostream>
#include <chrono>
#include <filesystem>

int main(int argc, char* argv[]) {
    int num_symbols = 20;
    int num_days = 3780; // 15 years for walk-forward
    int seed = 42;
    std::string output_dir = "./output/walk_forward";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--symbols" && i + 1 < argc) num_symbols = std::stoi(argv[++i]);
        else if (arg == "--days" && i + 1 < argc) num_days = std::stoi(argv[++i]);
        else if (arg == "--seed" && i + 1 < argc) seed = std::stoi(argv[++i]);
        else if (arg == "--output" && i + 1 < argc) output_dir = argv[++i];
    }

    std::cout << std::string(60, '=') << "\n";
    std::cout << "WALK-FORWARD VALIDATION\n";
    std::cout << std::string(60, '=') << "\n\n";

    // Generate data
    auto data = bt::DataGenerator::generate_universe(num_symbols, num_days, 0.08, 0.20, seed);
    std::cout << "Data: " << data.symbols().size() << " symbols x " << num_days << " days\n";

    // Generate walk-forward windows
    auto windows = bt::WalkForwardValidator::generate_windows(
        num_days,
        504,  // 2-year training
        126,  // 6-month test
        63    // 3-month step
    );
    std::cout << "Windows: " << windows.size() << " (2yr train, 6mo test, 3mo step)\n\n";

    bt::BacktestConfig config;
    config.initial_capital = 1'000'000.0;
    config.commission_rate = 0.001;
    config.slippage_bps = 5.0;
    config.volatility_sizing = true;
    config.vol_target = 0.15;
    config.max_position_pct = 0.10;
    config.max_drawdown_pct = 0.50; // Relaxed for individual windows

    auto t0 = std::chrono::high_resolution_clock::now();

    // Run walk-forward with OpenMP parallel windows
    auto results = bt::WalkForwardValidator::run(windows,
        [&](size_t start, size_t end) -> bt::PerformanceMetrics {
            auto strategy = std::make_shared<bt::MomentumStrategy>(252, 21, 10, 21);
            bt::BacktestEngine engine(config, strategy, data);
            return engine.run(start, end);
        }
    );

    auto t1 = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(t1 - t0).count();

    // Print results
    bt::WalkForwardValidator::print_summary(results);

    std::cout << "Total runtime: " << std::fixed << std::setprecision(1) << elapsed << "s\n";

    #ifdef _OPENMP
    std::cout << "OpenMP threads: " << omp_get_max_threads() << "\n";
    #endif

    // Export
    std::filesystem::create_directories(output_dir);
    std::ofstream f(output_dir + "/walk_forward_results.csv");
    f << "window,train_sharpe,test_sharpe,train_return,test_return,test_maxdd\n";
    for (const auto& r : results) {
        f << r.window_id << ","
          << std::fixed << std::setprecision(4) << r.train_sharpe << ","
          << r.test_sharpe << ","
          << r.train_return << ","
          << r.test_return << ","
          << r.test_metrics.max_drawdown << "\n";
    }
    std::cout << "Results written to: " << output_dir << "/walk_forward_results.csv\n";

    return 0;
}
