#include "test_framework.h"
#include "strategies/momentum.h"
#include "data/data_generator.h"

using namespace bt;

TEST(momentum_signals_on_rebalance_day) {
    auto data = DataGenerator::generate_universe(10, 504, 0.08, 0.20, 42);
    MomentumStrategy strat(252, 21, 5, 21);
    BacktestConfig config;

    // Bar 0 should produce signals (0 % 21 == 0) but not enough lookback
    auto signals = strat.generate_signals(data, 0, config);
    ASSERT_EQ(static_cast<int>(signals.size()), 0);

    // Bar 294 should produce signals (294 > 252 + 21, 294 % 21 == 0)
    signals = strat.generate_signals(data, 294, config);
    ASSERT_GT(static_cast<int>(signals.size()), 0);
    ASSERT_TRUE(signals.size() <= 5); // top_n = 5

    // All signals should be LONG with positive target_weight
    for (const auto& sig : signals) {
        ASSERT_TRUE(sig.direction == Signal::Direction::LONG);
        ASSERT_GT(sig.target_weight, 0.0);
    }
}

TEST(momentum_no_signals_off_rebalance) {
    auto data = DataGenerator::generate_universe(5, 504);
    MomentumStrategy strat(252, 21, 5, 21);
    BacktestConfig config;

    // Bar 295 is not a rebalance day (295 % 21 != 0)
    auto signals = strat.generate_signals(data, 295, config);
    ASSERT_EQ(static_cast<int>(signals.size()), 0);
}

TEST(momentum_excludes_benchmark) {
    auto data = DataGenerator::generate_universe(5, 504);
    MomentumStrategy strat(252, 21, 5, 21);
    BacktestConfig config;

    auto signals = strat.generate_signals(data, 294, config);
    for (const auto& sig : signals) {
        ASSERT_TRUE(sig.symbol != "SPY");
    }
}
