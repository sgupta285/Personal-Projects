#include "test_framework.h"
#include "utils/metrics.h"

using namespace bt;

TEST(metrics_basic_computation) {
    // Create simple equity curve: 100 -> 110 over 252 days
    std::vector<PortfolioSnapshot> snaps;
    for (int i = 0; i <= 252; ++i) {
        double eq = 100.0 + 10.0 * (static_cast<double>(i) / 252.0);
        double ret = (i > 0) ? (eq / (100.0 + 10.0 * (static_cast<double>(i - 1) / 252.0)) - 1.0) : 0.0;
        snaps.push_back({static_cast<int64_t>(i), eq, eq, 0, ret, 0, 0});
    }

    std::vector<TradeRecord> trades;
    std::vector<double> bm_returns(252, 0.0003); // Flat benchmark

    auto m = MetricsCalculator::compute(snaps, trades, bm_returns);

    ASSERT_GT(m.total_return, 0.0);
    ASSERT_GT(m.annualized_return, 0.0);
    ASSERT_GT(m.sharpe_ratio, 0.0);
    ASSERT_LT(m.max_drawdown, 0.5);
    ASSERT_GT(m.annualized_volatility, 0.0);
}

TEST(metrics_drawdown) {
    // Equity: 100 -> 120 -> 90 -> 110
    std::vector<PortfolioSnapshot> snaps = {
        {0, 100, 100, 0, 0.0, 0, 0},
        {1, 120, 120, 0, 0.2, 0, 0},
        {2, 90, 90, 0, -0.25, 0, 0},
        {3, 110, 110, 0, 0.222, 0, 0},
    };

    auto m = MetricsCalculator::compute(snaps, {}, {});
    // Max drawdown should be (120 - 90) / 120 = 25%
    ASSERT_NEAR(m.max_drawdown, 0.25, 0.01);
}

TEST(metrics_win_rate) {
    std::vector<PortfolioSnapshot> snaps = {
        {0, 100, 100, 0, 0, 0, 0},
        {1, 100, 100, 0, 0, 0, 0},
    };

    std::vector<TradeRecord> trades = {
        {"A", Order::Side::SELL, 100, 10.0, 12.0, 200.0, 0.2, 10, 0, 1},  // Win
        {"B", Order::Side::SELL, 100, 10.0, 12.0, 200.0, 0.2, 5, 0, 1},   // Win
        {"C", Order::Side::SELL, 100, 10.0, 8.0, -200.0, -0.2, 7, 0, 1},  // Loss
    };

    auto m = MetricsCalculator::compute(snaps, trades, {});
    ASSERT_NEAR(m.win_rate, 2.0 / 3.0, 0.01);
    ASSERT_EQ(m.total_trades, 3);
    ASSERT_EQ(m.winning_trades, 2);
    ASSERT_EQ(m.losing_trades, 1);
}

TEST(metrics_empty_data) {
    std::vector<PortfolioSnapshot> snaps;
    auto m = MetricsCalculator::compute(snaps, {}, {});
    ASSERT_NEAR(m.total_return, 0.0, 0.001);
    ASSERT_NEAR(m.sharpe_ratio, 0.0, 0.001);
}
