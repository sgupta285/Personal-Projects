#include "test_framework.h"
#include "engine/execution.h"

using namespace bt;

TEST(slippage_increases_with_participation) {
    ExecutionModel exec(5.0, 0.001);

    double slip_small = exec.compute_slippage(100.0, 1'000'000, 100);
    double slip_large = exec.compute_slippage(100.0, 1'000'000, 100'000);

    ASSERT_GT(slip_large, slip_small);
    ASSERT_GT(slip_small, 0.0);
    ASSERT_LT(slip_large, 0.01); // Capped at 1%
}

TEST(commission_proportional_to_value) {
    ExecutionModel exec(5.0, 0.001);

    double comm1 = exec.compute_commission(100.0, 100);
    double comm2 = exec.compute_commission(100.0, 200);

    ASSERT_NEAR(comm2, comm1 * 2.0, 0.01);
}

TEST(volatility_position_sizing) {
    double equity = 1'000'000.0;
    double price = 100.0;
    double vol_target = 0.15;
    double max_pct = 0.10;

    // High vol stock → smaller position
    int size_high_vol = ExecutionModel::compute_position_size(equity, price, 0.40, vol_target, max_pct);
    // Low vol stock → larger position (but capped)
    int size_low_vol = ExecutionModel::compute_position_size(equity, price, 0.10, vol_target, max_pct);

    ASSERT_GT(size_low_vol, size_high_vol);
    ASSERT_GT(size_high_vol, 0);

    // Position should respect max_pct cap
    double notional = size_low_vol * price;
    ASSERT_TRUE(notional <= equity * max_pct * 1.01); // Allow tiny float error
}

TEST(risk_manager_drawdown_stop) {
    RiskManager rm(0.20);

    ASSERT_FALSE(rm.check_drawdown(100'000));
    ASSERT_FALSE(rm.check_drawdown(110'000)); // New peak
    ASSERT_FALSE(rm.check_drawdown(95'000));  // -13.6%, below 20%
    ASSERT_TRUE(rm.check_drawdown(87'000));   // -20.9%, triggers stop

    ASSERT_TRUE(rm.is_stopped());

    rm.reset();
    ASSERT_FALSE(rm.is_stopped());
}
