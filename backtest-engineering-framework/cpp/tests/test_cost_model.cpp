#include "bef/cost_model.hpp"
#include "bef/fill_simulator.hpp"

#include <cassert>

int main() {
    bef::CostInput input{
        .mid_price = 100.0,
        .quantity = 100.0,
        .spread_bps = 5.0,
        .volatility_bps = 20.0,
        .participation_rate = 0.10,
        .commission_per_share = 0.002,
        .route_fee_bps = 0.5,
        .latency_ms = 10.0,
    };

    const auto m0 = bef::estimate_costs(bef::ExecutionTier::M0, input);
    const auto m5 = bef::estimate_costs(bef::ExecutionTier::M5, input);
    assert(m5.total() > m0.total());

    const auto buy_fill = bef::simulate_fill(bef::ExecutionTier::M3, input, true);
    const auto sell_fill = bef::simulate_fill(bef::ExecutionTier::M3, input, false);
    assert(buy_fill.executed_price > input.mid_price);
    assert(sell_fill.executed_price < input.mid_price);
    return 0;
}
