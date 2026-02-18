#pragma once

#include "engine/types.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace bt {

class MarketData {
public:
    void add_symbol(const std::string& symbol, const std::vector<Bar>& bars) {
        data_[symbol] = bars;
        // Sort by timestamp
        std::sort(data_[symbol].begin(), data_[symbol].end(),
            [](const Bar& a, const Bar& b) { return a.timestamp < b.timestamp; });
    }

    const std::vector<Bar>& get_bars(const std::string& symbol) const {
        auto it = data_.find(symbol);
        if (it == data_.end()) throw std::runtime_error("Symbol not found: " + symbol);
        return it->second;
    }

    std::vector<std::string> symbols() const {
        std::vector<std::string> syms;
        for (const auto& [s, _] : data_) syms.push_back(s);
        std::sort(syms.begin(), syms.end());
        return syms;
    }

    size_t num_bars(const std::string& symbol) const {
        auto it = data_.find(symbol);
        return (it != data_.end()) ? it->second.size() : 0;
    }

    bool has_symbol(const std::string& symbol) const {
        return data_.find(symbol) != data_.end();
    }

    // Get prices at a specific bar index across all symbols
    std::unordered_map<std::string, double> prices_at(size_t bar_index) const {
        std::unordered_map<std::string, double> prices;
        for (const auto& [sym, bars] : data_) {
            if (bar_index < bars.size()) {
                prices[sym] = bars[bar_index].adj_close;
            }
        }
        return prices;
    }

    // Compute rolling return for a symbol
    double rolling_return(const std::string& symbol, size_t end_idx, int period) const {
        const auto& bars = get_bars(symbol);
        if (end_idx < static_cast<size_t>(period) || end_idx >= bars.size()) return 0.0;
        double end_price = bars[end_idx].adj_close;
        double start_price = bars[end_idx - period].adj_close;
        return (start_price > 0.0) ? (end_price / start_price - 1.0) : 0.0;
    }

    // Compute rolling volatility (annualized)
    double rolling_volatility(const std::string& symbol, size_t end_idx, int period) const {
        const auto& bars = get_bars(symbol);
        if (end_idx < static_cast<size_t>(period) || end_idx >= bars.size()) return 0.0;

        std::vector<double> returns;
        returns.reserve(period);
        for (size_t i = end_idx - period + 1; i <= end_idx; ++i) {
            if (bars[i-1].adj_close > 0.0) {
                returns.push_back(bars[i].adj_close / bars[i-1].adj_close - 1.0);
            }
        }

        if (returns.size() < 2) return 0.0;
        double mean = 0.0;
        for (double r : returns) mean += r;
        mean /= returns.size();

        double var = 0.0;
        for (double r : returns) var += (r - mean) * (r - mean);
        var /= (returns.size() - 1);

        return std::sqrt(var * 252.0);
    }

    // Load from CSV: date,open,high,low,close,volume,adj_close
    static MarketData load_csv(const std::string& filepath, const std::string& symbol) {
        MarketData md;
        std::vector<Bar> bars;

        std::ifstream file(filepath);
        if (!file.is_open()) throw std::runtime_error("Cannot open: " + filepath);

        std::string line;
        std::getline(file, line); // skip header

        while (std::getline(file, line)) {
            if (line.empty()) continue;
            std::istringstream ss(line);
            std::string token;
            Bar bar{};

            std::getline(ss, token, ','); bar.timestamp = std::stoll(token);
            std::getline(ss, token, ','); bar.open = std::stod(token);
            std::getline(ss, token, ','); bar.high = std::stod(token);
            std::getline(ss, token, ','); bar.low = std::stod(token);
            std::getline(ss, token, ','); bar.close = std::stod(token);
            std::getline(ss, token, ','); bar.volume = std::stod(token);
            std::getline(ss, token, ','); bar.adj_close = std::stod(token);

            bars.push_back(bar);
        }

        md.add_symbol(symbol, bars);
        return md;
    }

    // Get common date range across all symbols
    std::pair<size_t, size_t> common_range() const {
        size_t min_size = SIZE_MAX;
        for (const auto& [_, bars] : data_) {
            min_size = std::min(min_size, bars.size());
        }
        return {0, min_size > 0 ? min_size - 1 : 0};
    }

private:
    std::unordered_map<std::string, std::vector<Bar>> data_;
};

} // namespace bt
