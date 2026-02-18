#pragma once

#include "strategies/momentum.h"
#include <cmath>

namespace bt {

// Mean reversion: buy oversold stocks (low z-score), sell overbought
class MeanReversionStrategy : public Strategy {
public:
    MeanReversionStrategy(int lookback = 20, double entry_z = -2.0, double exit_z = 0.0, int rebalance_freq = 5)
        : lookback_(lookback), entry_z_(entry_z), exit_z_(exit_z), rebalance_freq_(rebalance_freq) {}

    std::string name() const override { return "MeanReversion"; }

    std::vector<Signal> generate_signals(
        const MarketData& data, size_t bar_index, const BacktestConfig& config
    ) override {
        std::vector<Signal> signals;
        if (bar_index % rebalance_freq_ != 0) return signals;
        if (bar_index < static_cast<size_t>(lookback_ + 5)) return signals;

        auto syms = data.symbols();

        for (const auto& sym : syms) {
            if (sym == "SPY") continue;

            const auto& bars = data.get_bars(sym);
            if (bar_index >= bars.size()) continue;

            // Compute z-score of current price vs rolling mean
            double sum = 0.0, sum_sq = 0.0;
            int count = 0;
            for (size_t i = bar_index - lookback_; i < bar_index; ++i) {
                double p = bars[i].adj_close;
                sum += p;
                sum_sq += p * p;
                count++;
            }
            if (count < 2) continue;

            double mean = sum / count;
            double variance = (sum_sq / count) - (mean * mean);
            if (variance <= 0.0) continue;
            double stddev = std::sqrt(variance);
            double z = (bars[bar_index].adj_close - mean) / stddev;

            double vol = data.rolling_volatility(sym, bar_index, 20);

            if (z <= entry_z_) {
                // Oversold — long signal
                double weight = config.max_position_pct * 0.5;
                if (config.volatility_sizing && vol > 0.0) {
                    weight = std::min((config.vol_target / vol) * 0.1, config.max_position_pct);
                }
                signals.push_back({
                    Signal::Direction::LONG,
                    std::abs(z) / 4.0, weight, sym,
                    static_cast<int64_t>(bar_index)
                });
            } else if (z >= -exit_z_ + 2.0) {
                // Overbought — flat
                signals.push_back({
                    Signal::Direction::FLAT,
                    z / 4.0, 0.0, sym,
                    static_cast<int64_t>(bar_index)
                });
            }
        }

        return signals;
    }

private:
    int lookback_;
    double entry_z_;
    double exit_z_;
    int rebalance_freq_;
};

} // namespace bt
