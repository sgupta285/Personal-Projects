#pragma once

#include "engine/types.h"
#include <unordered_map>
#include <vector>
#include <string>

namespace bt {

class Portfolio {
public:
    explicit Portfolio(double initial_capital);

    // Order execution
    Fill execute_fill(const Order& order, double market_price, double slippage, double commission);

    // State queries
    double equity(const std::unordered_map<std::string, double>& prices) const;
    double cash() const { return cash_; }
    double positions_value(const std::unordered_map<std::string, double>& prices) const;
    int num_positions() const;
    const Position& get_position(const std::string& symbol) const;
    bool has_position(const std::string& symbol) const;
    std::vector<std::string> position_symbols() const;

    // Snapshot
    PortfolioSnapshot snapshot(int64_t ts, const std::unordered_map<std::string, double>& prices, double prev_equity);

    // Trade tracking
    const std::vector<TradeRecord>& trade_history() const { return trades_; }
    double initial_capital() const { return initial_capital_; }

    void reset(double capital);

private:
    double initial_capital_;
    double cash_;
    std::unordered_map<std::string, Position> positions_;
    std::vector<TradeRecord> trades_;
    static const Position empty_position_;
};

} // namespace bt
