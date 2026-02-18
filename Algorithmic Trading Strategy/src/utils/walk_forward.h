#pragma once

#include "engine/types.h"
#include "data/market_data.h"
#include "strategies/momentum.h"
#include <vector>
#include <functional>
#include <iostream>
#include <iomanip>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace bt {

struct WalkForwardWindow {
    size_t train_start;
    size_t train_end;
    size_t test_start;
    size_t test_end;
    int window_id;
};

struct WalkForwardResult {
    int window_id;
    PerformanceMetrics train_metrics;
    PerformanceMetrics test_metrics;
    double train_sharpe;
    double test_sharpe;
    double train_return;
    double test_return;
};

class WalkForwardValidator {
public:
    // Generate walk-forward windows
    static std::vector<WalkForwardWindow> generate_windows(
        size_t total_bars,
        int train_days = 504,     // 2 years training
        int test_days = 126,      // 6 months test (OOS)
        int step_days = 63        // 3 months step
    ) {
        std::vector<WalkForwardWindow> windows;
        int id = 0;

        for (size_t start = 0; start + train_days + test_days <= total_bars; start += step_days) {
            WalkForwardWindow w;
            w.window_id = id++;
            w.train_start = start;
            w.train_end = start + train_days - 1;
            w.test_start = start + train_days;
            w.test_end = std::min(start + train_days + test_days - 1, total_bars - 1);
            windows.push_back(w);
        }

        return windows;
    }

    // Run walk-forward with parallel window evaluation
    static std::vector<WalkForwardResult> run(
        const std::vector<WalkForwardWindow>& windows,
        std::function<PerformanceMetrics(size_t, size_t)> run_backtest
    ) {
        std::vector<WalkForwardResult> results(windows.size());

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < windows.size(); ++i) {
            const auto& w = windows[i];

            auto train_metrics = run_backtest(w.train_start, w.train_end);
            auto test_metrics = run_backtest(w.test_start, w.test_end);

            WalkForwardResult r;
            r.window_id = w.window_id;
            r.train_metrics = train_metrics;
            r.test_metrics = test_metrics;
            r.train_sharpe = train_metrics.sharpe_ratio;
            r.test_sharpe = test_metrics.sharpe_ratio;
            r.train_return = train_metrics.annualized_return;
            r.test_return = test_metrics.annualized_return;

            results[i] = r;
        }

        return results;
    }

    // Print walk-forward summary
    static void print_summary(const std::vector<WalkForwardResult>& results) {
        std::cout << "\n" << std::string(80, '=') << "\n";
        std::cout << "WALK-FORWARD VALIDATION RESULTS\n";
        std::cout << std::string(80, '=') << "\n\n";

        std::cout << std::setw(8) << "Window"
                  << std::setw(15) << "Train Sharpe"
                  << std::setw(15) << "Test Sharpe"
                  << std::setw(15) << "Train Return"
                  << std::setw(15) << "Test Return"
                  << std::setw(15) << "Test MaxDD"
                  << "\n";
        std::cout << std::string(83, '-') << "\n";

        double avg_train_sharpe = 0, avg_test_sharpe = 0;
        double avg_train_ret = 0, avg_test_ret = 0;
        int positive_oos = 0;

        for (const auto& r : results) {
            std::cout << std::setw(8) << r.window_id
                      << std::setw(15) << std::fixed << std::setprecision(2) << r.train_sharpe
                      << std::setw(15) << r.test_sharpe
                      << std::setw(14) << std::setprecision(1) << (r.train_return * 100) << "%"
                      << std::setw(14) << (r.test_return * 100) << "%"
                      << std::setw(14) << (r.test_metrics.max_drawdown * 100) << "%"
                      << "\n";

            avg_train_sharpe += r.train_sharpe;
            avg_test_sharpe += r.test_sharpe;
            avg_train_ret += r.train_return;
            avg_test_ret += r.test_return;
            if (r.test_sharpe > 0) positive_oos++;
        }

        int n = static_cast<int>(results.size());
        std::cout << std::string(83, '-') << "\n";
        std::cout << std::setw(8) << "AVG"
                  << std::setw(15) << std::setprecision(2) << avg_train_sharpe / n
                  << std::setw(15) << avg_test_sharpe / n
                  << std::setw(14) << std::setprecision(1) << (avg_train_ret / n * 100) << "%"
                  << std::setw(14) << (avg_test_ret / n * 100) << "%"
                  << "\n\n";

        std::cout << "Positive OOS Sharpe: " << positive_oos << "/" << n
                  << " (" << std::setprecision(0) << (100.0 * positive_oos / n) << "%)\n";

        double sharpe_decay = (avg_train_sharpe > 0)
            ? (1.0 - avg_test_sharpe / avg_train_sharpe) * 100.0 : 0.0;
        std::cout << "Sharpe decay (IS->OOS): " << std::setprecision(1) << sharpe_decay << "%\n";
        std::cout << std::string(80, '=') << "\n\n";
    }
};

} // namespace bt
