#include "bef/cost_model.hpp"

#include <algorithm>
#include <cmath>

namespace bef {

namespace {

double tier_multiplier(ExecutionTier tier) {
    switch (tier) {
        case ExecutionTier::M0: return 0.0;
        case ExecutionTier::M1: return 0.35;
        case ExecutionTier::M2: return 0.65;
        case ExecutionTier::M3: return 1.0;
        case ExecutionTier::M4: return 1.35;
        case ExecutionTier::M5: return 1.75;
    }
    return 1.0;
}

}  // namespace

double CostBreakdown::total() const {
    return commission + spread_cost + impact_cost + latency_cost + route_fee;
}

CostBreakdown estimate_costs(ExecutionTier tier, const CostInput& input) {
    const double px = std::max(0.01, input.mid_price);
    const double qty = std::max(0.0, input.quantity);
    const double multiplier = tier_multiplier(tier);
    const double spread_fraction = input.spread_bps / 10000.0;
    const double volatility_fraction = input.volatility_bps / 10000.0;
    const double participation = std::max(0.0, input.participation_rate);

    CostBreakdown result;
    result.commission = qty * std::max(0.0, input.commission_per_share);
    result.spread_cost = px * qty * 0.5 * spread_fraction * multiplier;
    result.impact_cost = px * qty * (0.25 * std::sqrt(participation) + 0.15 * volatility_fraction) * multiplier;
    result.latency_cost = px * qty * volatility_fraction * (input.latency_ms / 1000.0) * 0.05 * multiplier;
    result.route_fee = px * qty * (input.route_fee_bps / 10000.0) * multiplier;
    return result;
}

double fill_price(ExecutionTier tier, const CostInput& input, bool is_buy) {
    const auto costs = estimate_costs(tier, input);
    const double per_share = input.quantity <= 0.0 ? 0.0 : costs.total() / input.quantity;
    return is_buy ? input.mid_price + per_share : input.mid_price - per_share;
}

}  // namespace bef
