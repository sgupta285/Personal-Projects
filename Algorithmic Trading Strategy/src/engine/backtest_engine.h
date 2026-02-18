#pragma once

#include "engine/types.h"
#include "engine/portfolio.h"
#include "engine/execution.h"
#include "data/market_data.h"
#include "strategies/momentum.h"
#include "utils/metrics.h"
#include "utils/csv_writer.h"
#include <vector>
#include <memory>
#include <iostream>
#include <chrono>
#include <cmath>

namespace bt {

class BacktestEngine {
public:
    BacktestEngine(
        const BacktestConfig& config,
        std::shared_ptr<Strategy> strategy,
        const MarketData& data
    ) : config_(config),
        strategy_(std::move(strategy)),
        data_(data),
        portfolio_(config.initial_capital),
        execution_(config.slippage_bps, config.commission_rate),
        risk_mgr_(config.max_drawdown_pct) {}

    // Run full backtest over a date range
    PerformanceMetrics run(size_t start_bar = 0, size_t end_bar = 0) {
        auto t0 = std::chrono::high_resolution_clock::now();

        auto [range_start, range_end] = data_.common_range();
        if (start_bar > 0) range_start = start_bar;
        if (end_bar > 0) range_end = end_bar;

        portfolio_.reset(config_.initial_capital);
        risk_mgr_.reset();
        snapshots_.clear();
        benchmark_returns_.clear();

        double prev_equity = config_.initial_capital;
        double peak_equity = config_.initial_capital;

        // Pre-compute benchmark returns
        if (data_.has_symbol("SPY")) {
            const auto& spy = data_.get_bars("SPY");
            for (size_t i = range_start + 1; i <= range_end && i < spy.size(); ++i) {
                double ret = (spy[i-1].adj_close > 0.0) ?
                    spy[i].adj_close / spy[i-1].adj_close - 1.0 : 0.0;
                benchmark_returns_.push_back(ret);
            }
        }

        for (size_t bar = range_start; bar <= range_end; ++bar) {
            auto prices = data_.prices_at(bar);

            // Check risk limits
            double eq = portfolio_.equity(prices);
            if (risk_mgr_.check_drawdown(eq)) {
                // Liquidate all positions
                liquidate_all(prices, bar);
                break;
            }

            // Generate signals
            auto signals = strategy_->generate_signals(data_, bar, config_);

            // Process signals into orders
            process_signals(signals, prices, bar);

            // Record snapshot
            auto snap = portfolio_.snapshot(
                data_.get_bars(data_.symbols()[0])[bar].timestamp,
                prices, prev_equity
            );

            // Track drawdown
            if (snap.equity > peak_equity) peak_equity = snap.equity;
            snap.drawdown = (peak_equity > 0.0) ? 1.0 - snap.equity / peak_equity : 0.0;

            snapshots_.push_back(snap);
            prev_equity = snap.equity;
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        auto metrics = MetricsCalculator::compute(
            snapshots_, portfolio_.trade_history(), benchmark_returns_
        );

        if (elapsed_ms > 0.0) {
            std::cout << "[" << strategy_->name() << "] Backtest completed in "
                      << std::fixed << std::setprecision(1) << elapsed_ms << " ms"
                      << " (" << (range_end - range_start + 1) << " bars)\n";
        }

        return metrics;
    }

    // Accessors
    const std::vector<PortfolioSnapshot>& snapshots() const { return snapshots_; }
    const std::vector<TradeRecord>& trades() const { return portfolio_.trade_history(); }
    const std::vector<double>& benchmark_returns() const { return benchmark_returns_; }
    const Portfolio& portfolio() const { return portfolio_; }

    // Export results
    void export_results(const std::string& output_dir, const PerformanceMetrics& metrics) const {
        CsvWriter::write_snapshots(output_dir + "/equity_curve.csv", snapshots_);
        CsvWriter::write_trades(output_dir + "/trades.csv", portfolio_.trade_history());
        CsvWriter::write_metrics(output_dir + "/metrics.csv", metrics, strategy_->name());
    }

private:
    void process_signals(
        const std::vector<Signal>& signals,
        const std::unordered_map<std::string, double>& prices,
        size_t bar_index
    ) {
        // Build target portfolio from signals
        std::unordered_map<std::string, double> target_weights;
        for (const auto& sig : signals) {
            if (sig.direction == Signal::Direction::LONG) {
                target_weights[sig.symbol] = sig.target_weight;
            } else if (sig.direction == Signal::Direction::FLAT) {
                target_weights[sig.symbol] = 0.0;
            }
        }

        double equity = portfolio_.equity(prices);

        // Close positions not in target
        for (const auto& sym : portfolio_.position_symbols()) {
            if (target_weights.find(sym) == target_weights.end()) {
                target_weights[sym] = 0.0; // Close
            }
        }

        // Execute rebalance
        for (const auto& [sym, target_wt] : target_weights) {
            auto pit = prices.find(sym);
            if (pit == prices.end() || pit->second <= 0.0) continue;

            double price = pit->second;
            int current_qty = portfolio_.has_position(sym) ? portfolio_.get_position(sym).quantity : 0;

            int target_qty;
            if (config_.volatility_sizing && target_wt > 0.0) {
                double vol = data_.rolling_volatility(sym, bar_index, 60);
                target_qty = ExecutionModel::compute_position_size(
                    equity, price, vol, config_.vol_target, config_.max_position_pct
                );
            } else {
                double target_notional = equity * target_wt;
                target_qty = static_cast<int>(std::floor(target_notional / price));
            }

            int delta = target_qty - current_qty;
            if (delta == 0) continue;

            // Determine volume for slippage calc
            double volume = 1'000'000; // Default
            if (data_.has_symbol(sym) && bar_index < data_.get_bars(sym).size()) {
                volume = data_.get_bars(sym)[bar_index].volume;
            }

            double slippage = execution_.compute_slippage(price, volume, delta);
            double commission = execution_.compute_commission(price, std::abs(delta));

            Order order;
            order.symbol = sym;
            order.side = (delta > 0) ? Order::Side::BUY : Order::Side::SELL;
            order.type = Order::Type::MARKET;
            order.quantity = std::abs(delta);
            order.limit_price = price;
            order.timestamp = static_cast<int64_t>(bar_index);

            try {
                portfolio_.execute_fill(order, price, slippage, commission);
            } catch (const std::exception& e) {
                // Insufficient cash — skip this order
            }
        }
    }

    void liquidate_all(const std::unordered_map<std::string, double>& prices, size_t bar_index) {
        for (const auto& sym : portfolio_.position_symbols()) {
            auto pit = prices.find(sym);
            if (pit == prices.end()) continue;

            const auto& pos = portfolio_.get_position(sym);
            if (pos.quantity == 0) continue;

            Order order;
            order.symbol = sym;
            order.side = (pos.quantity > 0) ? Order::Side::SELL : Order::Side::BUY;
            order.type = Order::Type::MARKET;
            order.quantity = std::abs(pos.quantity);
            order.limit_price = pit->second;
            order.timestamp = static_cast<int64_t>(bar_index);

            double slippage = execution_.compute_slippage(pit->second, 1'000'000, pos.quantity);
            double commission = execution_.compute_commission(pit->second, std::abs(pos.quantity));

            try {
                portfolio_.execute_fill(order, pit->second, slippage, commission);
            } catch (...) {}
        }
    }

    BacktestConfig config_;
    std::shared_ptr<Strategy> strategy_;
    const MarketData& data_;
    Portfolio portfolio_;
    ExecutionModel execution_;
    RiskManager risk_mgr_;
    std::vector<PortfolioSnapshot> snapshots_;
    std::vector<double> benchmark_returns_;
};

} // namespace bt
