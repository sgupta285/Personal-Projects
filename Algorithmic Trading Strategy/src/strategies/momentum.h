#pragma once

#include "engine/types.h"
#include "data/market_data.h"
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>
#include <cmath>

namespace bt {

// Strategy interface
class Strategy {
public:
    virtual ~Strategy() = default;
    virtual std::string name() const = 0;
    virtual std::vector<Signal> generate_signals(
        const MarketData& data, size_t bar_index, const BacktestConfig& config
    ) = 0;
};

// Cross-sectional momentum: rank stocks by trailing return, go long top quintile
class MomentumStrategy : public Strategy {
public:
    MomentumStrategy(int lookback = 252, int skip = 21, int top_n = 10, int rebalance_freq = 21)
        : lookback_(lookback), skip_(skip), top_n_(top_n), rebalance_freq_(rebalance_freq) {}

    std::string name() const override { return "Momentum"; }

    std::vector<Signal> generate_signals(
        const MarketData& data, size_t bar_index, const BacktestConfig& config
    ) override {
        std::vector<Signal> signals;

        // Only generate on rebalance days
        if (bar_index % rebalance_freq_ != 0) return signals;
        if (bar_index < static_cast<size_t>(lookback_ + skip_)) return signals;

        auto syms = data.symbols();
        struct RankedStock {
            std::string symbol;
            double momentum;
            double volatility;
        };

        std::vector<RankedStock> ranked;
        for (const auto& sym : syms) {
            if (sym == "SPY") continue; // Don't trade benchmark

            const auto& bars = data.get_bars(sym);
            if (bar_index >= bars.size()) continue;

            // Momentum signal: return from (t - lookback - skip) to (t - skip)
            // Skip recent period to avoid reversal effect
            size_t end_idx = bar_index - skip_;
            double mom = data.rolling_return(sym, end_idx, lookback_);
            double vol = data.rolling_volatility(sym, bar_index, 60);

            if (vol > 0.0 && std::isfinite(mom)) {
                ranked.push_back({sym, mom, vol});
            }
        }

        // Rank by momentum (descending)
        std::sort(ranked.begin(), ranked.end(),
            [](const RankedStock& a, const RankedStock& b) { return a.momentum > b.momentum; });

        // Top N = long signals
        int n_long = std::min(top_n_, static_cast<int>(ranked.size()));
        double weight = 1.0 / std::max(n_long, 1);

        for (int i = 0; i < n_long; ++i) {
            const auto& stock = ranked[i];
            if (stock.momentum <= 0.0) break; // Only positive momentum

            double vol_adj_weight = weight;
            if (config.volatility_sizing && stock.volatility > 0.0) {
                // Inverse-vol weighting
                vol_adj_weight = (config.vol_target / stock.volatility) / n_long;
                vol_adj_weight = std::min(vol_adj_weight, config.max_position_pct);
            }

            signals.push_back({
                Signal::Direction::LONG,
                stock.momentum,
                vol_adj_weight,
                stock.symbol,
                static_cast<int64_t>(bar_index)
            });
        }

        return signals;
    }

private:
    int lookback_;
    int skip_;
    int top_n_;
    int rebalance_freq_;
};

} // namespace bt
