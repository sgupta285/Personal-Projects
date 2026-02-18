#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <cmath>
#include <algorithm>

namespace bt {

struct Bar {
    int64_t timestamp;     // Unix epoch seconds
    double open;
    double high;
    double low;
    double close;
    double volume;
    double adj_close;

    double typical_price() const { return (high + low + close) / 3.0; }
    double true_range(double prev_close) const {
        return std::max({high - low, std::abs(high - prev_close), std::abs(low - prev_close)});
    }
};

struct Signal {
    enum class Direction { LONG, SHORT, FLAT };
    Direction direction;
    double strength;       // 0.0 to 1.0
    double target_weight;  // portfolio weight target
    std::string symbol;
    int64_t timestamp;
};

struct Order {
    enum class Side { BUY, SELL };
    enum class Type { MARKET, LIMIT };

    std::string symbol;
    Side side;
    Type type;
    int quantity;
    double limit_price;
    int64_t timestamp;
};

struct Fill {
    std::string symbol;
    Order::Side side;
    int quantity;
    double fill_price;
    double slippage;
    double commission;
    int64_t timestamp;
};

struct Position {
    std::string symbol;
    int quantity = 0;
    double avg_cost = 0.0;
    double unrealized_pnl = 0.0;
    double realized_pnl = 0.0;

    double market_value(double price) const { return quantity * price; }
    void update_unrealized(double price) {
        unrealized_pnl = (price - avg_cost) * quantity;
    }
};

struct PortfolioSnapshot {
    int64_t timestamp;
    double equity;
    double cash;
    double positions_value;
    double daily_return;
    double drawdown;
    int num_positions;
};

struct TradeRecord {
    std::string symbol;
    Order::Side side;
    int quantity;
    double entry_price;
    double exit_price;
    double pnl;
    double return_pct;
    int holding_days;
    int64_t entry_time;
    int64_t exit_time;
};

struct BacktestConfig {
    double initial_capital = 1'000'000.0;
    double commission_rate = 0.001;       // 10 bps
    double slippage_bps = 5.0;            // 5 bps
    double max_position_pct = 0.10;       // 10% max single position
    double max_drawdown_pct = 0.20;       // 20% max drawdown stop
    bool volatility_sizing = true;
    double vol_target = 0.15;             // 15% annualized vol target
    int lookback_window = 252;            // 1 year
    int rebalance_frequency = 21;         // Monthly rebalance
};

struct PerformanceMetrics {
    double total_return;
    double annualized_return;
    double sharpe_ratio;
    double sortino_ratio;
    double max_drawdown;
    double max_drawdown_duration_days;
    double calmar_ratio;
    double win_rate;
    double profit_factor;
    double avg_trade_return;
    double avg_winner;
    double avg_loser;
    int total_trades;
    int winning_trades;
    int losing_trades;
    double annualized_volatility;
    double downside_deviation;
    double skewness;
    double kurtosis;
    double var_95;
    double cvar_95;
    double turnover;
    double alpha;
    double beta;
    double information_ratio;
};

} // namespace bt
