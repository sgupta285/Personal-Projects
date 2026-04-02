#pragma once

#include <cstdint>

namespace bef {

enum class ExecutionTier : std::uint8_t {
    M0 = 0,
    M1 = 1,
    M2 = 2,
    M3 = 3,
    M4 = 4,
    M5 = 5,
};

struct CostInput {
    double mid_price;
    double quantity;
    double spread_bps;
    double volatility_bps;
    double participation_rate;
    double commission_per_share;
    double route_fee_bps;
    double latency_ms;
};

struct CostBreakdown {
    double commission = 0.0;
    double spread_cost = 0.0;
    double impact_cost = 0.0;
    double latency_cost = 0.0;
    double route_fee = 0.0;

    [[nodiscard]] double total() const;
};

CostBreakdown estimate_costs(ExecutionTier tier, const CostInput& input);

double fill_price(ExecutionTier tier, const CostInput& input, bool is_buy);

}  // namespace bef
