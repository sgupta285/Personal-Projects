#pragma once

#include "engine/types.h"
#include <vector>
#include <string>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <iostream>

namespace bt {

class CsvWriter {
public:
    static void write_snapshots(const std::string& filepath, const std::vector<PortfolioSnapshot>& snaps) {
        std::ofstream f(filepath);
        if (!f.is_open()) {
            std::cerr << "Cannot write to: " << filepath << "\n";
            return;
        }

        f << "timestamp,equity,cash,positions_value,daily_return,drawdown,num_positions\n";
        for (const auto& s : snaps) {
            f << s.timestamp << ","
              << std::fixed << std::setprecision(2) << s.equity << ","
              << s.cash << "," << s.positions_value << ","
              << std::setprecision(6) << s.daily_return << ","
              << s.drawdown << "," << s.num_positions << "\n";
        }

        std::cout << "Written " << snaps.size() << " snapshots to " << filepath << "\n";
    }

    static void write_trades(const std::string& filepath, const std::vector<TradeRecord>& trades) {
        std::ofstream f(filepath);
        if (!f.is_open()) return;

        f << "symbol,side,quantity,entry_price,exit_price,pnl,return_pct,holding_days,entry_time,exit_time\n";
        for (const auto& t : trades) {
            f << t.symbol << ","
              << (t.side == Order::Side::BUY ? "BUY" : "SELL") << ","
              << t.quantity << ","
              << std::fixed << std::setprecision(2) << t.entry_price << ","
              << t.exit_price << ","
              << t.pnl << ","
              << std::setprecision(4) << t.return_pct << ","
              << t.holding_days << ","
              << t.entry_time << "," << t.exit_time << "\n";
        }
    }

    static void write_metrics(const std::string& filepath, const PerformanceMetrics& m, const std::string& strategy) {
        std::ofstream f(filepath);
        if (!f.is_open()) return;

        f << "metric,value\n";
        f << "strategy," << strategy << "\n";
        f << "total_return," << std::fixed << std::setprecision(4) << m.total_return << "\n";
        f << "annualized_return," << m.annualized_return << "\n";
        f << "sharpe_ratio," << std::setprecision(2) << m.sharpe_ratio << "\n";
        f << "sortino_ratio," << m.sortino_ratio << "\n";
        f << "calmar_ratio," << m.calmar_ratio << "\n";
        f << "max_drawdown," << std::setprecision(4) << m.max_drawdown << "\n";
        f << "max_drawdown_duration_days," << m.max_drawdown_duration_days << "\n";
        f << "annualized_volatility," << m.annualized_volatility << "\n";
        f << "downside_deviation," << m.downside_deviation << "\n";
        f << "win_rate," << m.win_rate << "\n";
        f << "profit_factor," << std::setprecision(2) << m.profit_factor << "\n";
        f << "total_trades," << m.total_trades << "\n";
        f << "winning_trades," << m.winning_trades << "\n";
        f << "losing_trades," << m.losing_trades << "\n";
        f << "avg_trade_return," << std::setprecision(4) << m.avg_trade_return << "\n";
        f << "avg_winner," << std::setprecision(2) << m.avg_winner << "\n";
        f << "avg_loser," << m.avg_loser << "\n";
        f << "skewness," << std::setprecision(3) << m.skewness << "\n";
        f << "kurtosis," << m.kurtosis << "\n";
        f << "var_95," << std::setprecision(4) << m.var_95 << "\n";
        f << "cvar_95," << m.cvar_95 << "\n";
        f << "alpha," << m.alpha << "\n";
        f << "beta," << std::setprecision(2) << m.beta << "\n";
        f << "information_ratio," << m.information_ratio << "\n";
        f << "turnover," << m.turnover << "\n";
    }

    static void print_metrics(const PerformanceMetrics& m, const std::string& strategy_name) {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "PERFORMANCE REPORT: " << strategy_name << "\n";
        std::cout << std::string(60, '=') << "\n\n";

        std::cout << "--- Returns ---\n";
        std::cout << "  Total Return:        " << std::fixed << std::setprecision(1) << m.total_return * 100 << "%\n";
        std::cout << "  Annualized Return:   " << m.annualized_return * 100 << "%\n";
        std::cout << "  Annualized Vol:      " << m.annualized_volatility * 100 << "%\n";
        std::cout << "\n--- Risk-Adjusted ---\n";
        std::cout << "  Sharpe Ratio:        " << std::setprecision(2) << m.sharpe_ratio << "\n";
        std::cout << "  Sortino Ratio:       " << m.sortino_ratio << "\n";
        std::cout << "  Calmar Ratio:        " << m.calmar_ratio << "\n";
        std::cout << "  Information Ratio:   " << m.information_ratio << "\n";
        std::cout << "\n--- Drawdown ---\n";
        std::cout << "  Max Drawdown:        " << std::setprecision(1) << m.max_drawdown * 100 << "%\n";
        std::cout << "  Max DD Duration:     " << m.max_drawdown_duration_days << " days\n";
        std::cout << "\n--- Risk ---\n";
        std::cout << "  VaR (95%):           " << std::setprecision(2) << m.var_95 * 100 << "%\n";
        std::cout << "  CVaR (95%):          " << m.cvar_95 * 100 << "%\n";
        std::cout << "  Skewness:            " << std::setprecision(3) << m.skewness << "\n";
        std::cout << "  Excess Kurtosis:     " << m.kurtosis << "\n";
        std::cout << "  Alpha:               " << std::setprecision(2) << m.alpha * 100 << "%\n";
        std::cout << "  Beta:                " << m.beta << "\n";
        std::cout << "\n--- Trading ---\n";
        std::cout << "  Total Trades:        " << m.total_trades << "\n";
        std::cout << "  Win Rate:            " << std::setprecision(1) << m.win_rate * 100 << "%\n";
        std::cout << "  Profit Factor:       " << std::setprecision(2) << m.profit_factor << "\n";
        std::cout << "  Avg Winner:          $" << std::setprecision(0) << m.avg_winner << "\n";
        std::cout << "  Avg Loser:           $" << m.avg_loser << "\n";
        std::cout << "  Turnover:            " << std::setprecision(1) << m.turnover << "x\n";
        std::cout << "\n" << std::string(60, '=') << "\n\n";
    }
};

} // namespace bt
