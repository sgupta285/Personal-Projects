#pragma once

#include "engine/types.h"
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

namespace bt {

class ExecutionModel {
public:
    explicit ExecutionModel(double slippage_bps = 5.0, double commission_rate = 0.001)
        : slippage_bps_(slippage_bps), commission_rate_(commission_rate) {}

    double compute_slippage(double price, double volume, int quantity) const {
        // Market impact: base slippage + volume-dependent component
        double base_slip = slippage_bps_ / 10000.0;
        double participation = (volume > 0) ? static_cast<double>(std::abs(quantity)) / volume : 0.01;
        double impact = base_slip * (1.0 + std::sqrt(participation) * 2.0);
        return std::min(impact, 0.01); // Cap at 1%
    }

    double compute_commission(double price, int quantity) const {
        return std::abs(price * quantity) * commission_rate_;
    }

    // Volatility-adaptive position sizing
    static int compute_position_size(
        double equity, double price, double vol_20d,
        double vol_target, double max_position_pct
    ) {
        if (price <= 0.0 || vol_20d <= 0.0) return 0;

        // Target dollar vol per position = equity * vol_target / sqrt(252) / num_expected_positions
        double target_dollar_vol = equity * vol_target / std::sqrt(252.0);
        double position_dollar_vol = price * vol_20d;

        // Size to achieve target vol contribution
        double target_notional = target_dollar_vol / vol_20d;
        double max_notional = equity * max_position_pct;
        double notional = std::min(target_notional, max_notional);

        return static_cast<int>(std::floor(notional / price));
    }

private:
    double slippage_bps_;
    double commission_rate_;
};

// Risk manager with drawdown limits
class RiskManager {
public:
    explicit RiskManager(double max_drawdown_pct = 0.20)
        : max_drawdown_pct_(max_drawdown_pct), peak_equity_(0.0), is_stopped_(false) {}

    bool check_drawdown(double equity) {
        if (equity > peak_equity_) {
            peak_equity_ = equity;
        }
        double dd = 1.0 - (equity / peak_equity_);
        if (dd >= max_drawdown_pct_) {
            is_stopped_ = true;
        }
        return is_stopped_;
    }

    double current_drawdown(double equity) const {
        if (peak_equity_ <= 0.0) return 0.0;
        return 1.0 - (equity / peak_equity_);
    }

    bool is_stopped() const { return is_stopped_; }

    void reset() {
        peak_equity_ = 0.0;
        is_stopped_ = false;
    }

private:
    double max_drawdown_pct_;
    double peak_equity_;
    bool is_stopped_;
};

} // namespace bt
