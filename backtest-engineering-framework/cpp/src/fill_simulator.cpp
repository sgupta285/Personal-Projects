#include "bef/fill_simulator.hpp"

namespace bef {

FillResult simulate_fill(ExecutionTier tier, const CostInput& input, bool is_buy) {
    const auto costs = estimate_costs(tier, input);
    return FillResult{
        .executed_price = fill_price(tier, input, is_buy),
        .costs = costs,
    };
}

}  // namespace bef
