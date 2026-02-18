#include "engine/portfolio.h"
#include <cmath>
#include <stdexcept>

namespace bt {

const Position Portfolio::empty_position_ = {};

Portfolio::Portfolio(double initial_capital)
    : initial_capital_(initial_capital), cash_(initial_capital) {}

Fill Portfolio::execute_fill(const Order& order, double market_price, double slippage, double commission) {
    double fill_price = (order.side == Order::Side::BUY)
        ? market_price * (1.0 + slippage)
        : market_price * (1.0 - slippage);

    Fill fill;
    fill.symbol = order.symbol;
    fill.side = order.side;
    fill.quantity = order.quantity;
    fill.fill_price = fill_price;
    fill.slippage = std::abs(fill_price - market_price) * order.quantity;
    fill.commission = commission;
    fill.timestamp = order.timestamp;

    auto& pos = positions_[order.symbol];
    pos.symbol = order.symbol;

    if (order.side == Order::Side::BUY) {
        double cost = fill_price * order.quantity + commission;
        if (cost > cash_) {
            throw std::runtime_error("Insufficient cash for order");
        }
        double new_qty = pos.quantity + order.quantity;
        if (pos.quantity >= 0) {
            pos.avg_cost = (pos.avg_cost * pos.quantity + fill_price * order.quantity) / new_qty;
        } else {
            // Covering short
            double pnl = (pos.avg_cost - fill_price) * std::min(order.quantity, -pos.quantity);
            pos.realized_pnl += pnl;

            if (order.quantity > -pos.quantity) {
                pos.avg_cost = fill_price;
            }
        }
        pos.quantity = new_qty;
        cash_ -= cost;
    } else {
        // SELL
        double proceeds = fill_price * order.quantity - commission;
        if (pos.quantity > 0) {
            int close_qty = std::min(order.quantity, pos.quantity);
            double pnl = (fill_price - pos.avg_cost) * close_qty;
            pos.realized_pnl += pnl;

            trades_.push_back({
                order.symbol, order.side, close_qty,
                pos.avg_cost, fill_price, pnl,
                (fill_price - pos.avg_cost) / pos.avg_cost,
                0, // holding_days computed externally
                0, order.timestamp
            });
        }
        pos.quantity -= order.quantity;
        cash_ += proceeds;

        if (pos.quantity < 0) {
            pos.avg_cost = fill_price;
        }
    }

    // Clean up zero positions
    if (pos.quantity == 0) {
        positions_.erase(order.symbol);
    }

    return fill;
}

double Portfolio::equity(const std::unordered_map<std::string, double>& prices) const {
    double total = cash_;
    for (const auto& [sym, pos] : positions_) {
        auto it = prices.find(sym);
        if (it != prices.end()) {
            total += pos.quantity * it->second;
        }
    }
    return total;
}

double Portfolio::positions_value(const std::unordered_map<std::string, double>& prices) const {
    double total = 0.0;
    for (const auto& [sym, pos] : positions_) {
        auto it = prices.find(sym);
        if (it != prices.end()) {
            total += std::abs(pos.quantity * it->second);
        }
    }
    return total;
}

int Portfolio::num_positions() const {
    return static_cast<int>(positions_.size());
}

const Position& Portfolio::get_position(const std::string& symbol) const {
    auto it = positions_.find(symbol);
    return (it != positions_.end()) ? it->second : empty_position_;
}

bool Portfolio::has_position(const std::string& symbol) const {
    return positions_.find(symbol) != positions_.end();
}

std::vector<std::string> Portfolio::position_symbols() const {
    std::vector<std::string> syms;
    syms.reserve(positions_.size());
    for (const auto& [sym, _] : positions_) {
        syms.push_back(sym);
    }
    return syms;
}

PortfolioSnapshot Portfolio::snapshot(int64_t ts, const std::unordered_map<std::string, double>& prices, double prev_equity) {
    double eq = equity(prices);
    double daily_ret = (prev_equity > 0.0) ? (eq / prev_equity - 1.0) : 0.0;

    return PortfolioSnapshot{
        ts, eq, cash_, positions_value(prices),
        daily_ret, 0.0, // drawdown computed externally
        num_positions()
    };
}

void Portfolio::reset(double capital) {
    cash_ = capital;
    positions_.clear();
    trades_.clear();
    initial_capital_ = capital;
}

} // namespace bt
