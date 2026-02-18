/**
 * Algorithmic Trading Strategy Backtest Engine
 * Main entry point — runs momentum strategy on synthetic market data,
 * computes performance metrics, and exports results for Python analysis.
 *
 * Usage:
 *   ./backtest                    # Run with defaults
 *   ./backtest --symbols 30       # 30-stock universe
 *   ./backtest --days 2520        # 10 years of data
 *   ./backtest --output ./results # Export directory
 */

#include "engine/backtest_engine.h"
#include "data/data_generator.h"
#include "strategies/momentum.h"
#include "strategies/mean_reversion.h"
#include "utils/csv_writer.h"

#include <iostream>
#include <string>
#include <filesystem>
#include <memory>
#include <chrono>

namespace fs = std::filesystem;

struct CLIArgs {
    int num_symbols = 20;
    int num_days = 2520;   // 10 years
    double initial_capital = 1'000'000.0;
    std::string output_dir = "./output";
    bool run_mean_reversion = false;
    int seed = 42;
};

CLIArgs parse_args(int argc, char* argv[]) {
    CLIArgs args;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--symbols" && i + 1 < argc) args.num_symbols = std::stoi(argv[++i]);
        else if (arg == "--days" && i + 1 < argc) args.num_days = std::stoi(argv[++i]);
        else if (arg == "--capital" && i + 1 < argc) args.initial_capital = std::stod(argv[++i]);
        else if (arg == "--output" && i + 1 < argc) args.output_dir = argv[++i];
        else if (arg == "--seed" && i + 1 < argc) args.seed = std::stoi(argv[++i]);
        else if (arg == "--mean-reversion") args.run_mean_reversion = true;
        else if (arg == "--help") {
            std::cout << "Usage: backtest [options]\n"
                      << "  --symbols N      Number of stocks (default: 20)\n"
                      << "  --days N         Trading days (default: 2520)\n"
                      << "  --capital N      Initial capital (default: 1000000)\n"
                      << "  --output DIR     Output directory (default: ./output)\n"
                      << "  --seed N         Random seed (default: 42)\n"
                      << "  --mean-reversion Also run mean reversion strategy\n"
                      << "  --help           Show this help\n";
            exit(0);
        }
    }
    return args;
}

int main(int argc, char* argv[]) {
    auto args = parse_args(argc, argv);

    std::cout << std::string(60, '=') << "\n";
    std::cout << "ALGORITHMIC TRADING BACKTEST ENGINE\n";
    std::cout << std::string(60, '=') << "\n";
    std::cout << "Universe: " << args.num_symbols << " stocks + SPY benchmark\n";
    std::cout << "Period:   " << args.num_days << " trading days (~"
              << args.num_days / 252 << " years)\n";
    std::cout << "Capital:  $" << std::fixed << std::setprecision(0) << args.initial_capital << "\n";
    std::cout << std::string(60, '-') << "\n\n";

    // Generate synthetic market data
    auto t0 = std::chrono::high_resolution_clock::now();
    auto data = bt::DataGenerator::generate_universe(args.num_symbols, args.num_days, 0.08, 0.20, args.seed);
    auto t1 = std::chrono::high_resolution_clock::now();
    double gen_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    std::cout << "Data generated: " << data.symbols().size() << " symbols x "
              << args.num_days << " days in " << std::setprecision(1) << gen_ms << " ms\n\n";

    // Create output directory
    fs::create_directories(args.output_dir);

    // Configure backtest
    bt::BacktestConfig config;
    config.initial_capital = args.initial_capital;
    config.commission_rate = 0.001;
    config.slippage_bps = 5.0;
    config.max_position_pct = 0.10;
    config.max_drawdown_pct = 0.25;
    config.volatility_sizing = true;
    config.vol_target = 0.15;
    config.rebalance_frequency = 21;

    // --- Run Momentum Strategy ---
    {
        auto strategy = std::make_shared<bt::MomentumStrategy>(252, 21, 10, 21);
        bt::BacktestEngine engine(config, strategy, data);
        auto metrics = engine.run();

        bt::CsvWriter::print_metrics(metrics, "Momentum (12-1)");

        // Export
        std::string dir = args.output_dir + "/momentum";
        fs::create_directories(dir);
        engine.export_results(dir, metrics);
    }

    // --- Run Mean Reversion Strategy (optional) ---
    if (args.run_mean_reversion) {
        auto strategy = std::make_shared<bt::MeanReversionStrategy>(20, -2.0, 0.0, 5);
        bt::BacktestEngine engine(config, strategy, data);
        auto metrics = engine.run();

        bt::CsvWriter::print_metrics(metrics, "Mean Reversion (20d z-score)");

        std::string dir = args.output_dir + "/mean_reversion";
        fs::create_directories(dir);
        engine.export_results(dir, metrics);
    }

    std::cout << "Results exported to: " << args.output_dir << "/\n";
    return 0;
}
