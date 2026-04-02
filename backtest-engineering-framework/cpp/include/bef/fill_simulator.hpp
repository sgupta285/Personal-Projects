#pragma once

#include "bef/cost_model.hpp"

namespace bef {

struct FillResult {
    double executed_price;
    CostBreakdown costs;
};

FillResult simulate_fill(ExecutionTier tier, const CostInput& input, bool is_buy);

}  // namespace bef
