#pragma once

#include "data/market_data.h"
#include <random>
#include <cmath>
#include <string>
#include <vector>

namespace bt {

class DataGenerator {
public:
    // Generate synthetic daily bars with geometric Brownian motion + fat tails
    static MarketData generate_universe(
        int num_symbols,
        int num_days,
        double avg_annual_return = 0.08,
        double avg_annual_vol = 0.20,
        int seed = 42
    ) {
        MarketData md;
        std::mt19937 rng(seed);
        std::normal_distribution<double> norm(0.0, 1.0);
        std::uniform_real_distribution<double> ret_dist(0.02, 0.15);
        std::uniform_real_distribution<double> vol_dist(0.12, 0.40);
        std::uniform_real_distribution<double> price_dist(20.0, 500.0);

        // Generate SPY as benchmark
        auto spy_bars = generate_bars(rng, norm, num_days, 400.0, 0.10, 0.16, 50'000'000);
        md.add_symbol("SPY", spy_bars);

        // Generate individual stocks with some correlation to SPY
        for (int i = 0; i < num_symbols; ++i) {
            std::string sym = "SYM" + std::to_string(i + 1);
            double mu = ret_dist(rng);
            double sigma = vol_dist(rng);
            double start_price = price_dist(rng);
            double base_volume = 1'000'000.0 + rng() % 10'000'000;
            double beta = 0.5 + (rng() % 100) / 100.0; // 0.5 to 1.5

            auto bars = generate_correlated_bars(
                rng, norm, spy_bars, num_days, start_price,
                mu, sigma, base_volume, beta
            );
            md.add_symbol(sym, bars);
        }

        return md;
    }

private:
    static std::vector<Bar> generate_bars(
        std::mt19937& rng, std::normal_distribution<double>& norm,
        int num_days, double start_price, double annual_return,
        double annual_vol, double base_volume
    ) {
        std::vector<Bar> bars;
        bars.reserve(num_days);

        double daily_mu = annual_return / 252.0;
        double daily_sigma = annual_vol / std::sqrt(252.0);

        double price = start_price;
        int64_t ts = 946684800; // 2000-01-01

        for (int i = 0; i < num_days; ++i) {
            double z = norm(rng);
            // Add occasional fat tails (t-distribution approximation)
            if (std::abs(z) > 2.0) z *= 1.5;

            double ret = daily_mu + daily_sigma * z;
            double new_price = price * std::exp(ret);

            double intraday_vol = std::abs(daily_sigma * norm(rng));
            double high = new_price * (1.0 + intraday_vol);
            double low = new_price * (1.0 - intraday_vol);
            double open = price + (new_price - price) * (0.3 + 0.4 * (rng() % 100) / 100.0);
            double vol = base_volume * (0.5 + 1.5 * (rng() % 100) / 100.0);

            bars.push_back({ts, open, high, low, new_price, vol, new_price});
            price = new_price;
            ts += 86400; // Next day
        }

        return bars;
    }

    static std::vector<Bar> generate_correlated_bars(
        std::mt19937& rng, std::normal_distribution<double>& norm,
        const std::vector<Bar>& benchmark, int num_days, double start_price,
        double annual_return, double annual_vol, double base_volume, double beta
    ) {
        std::vector<Bar> bars;
        bars.reserve(num_days);

        double daily_mu = annual_return / 252.0;
        double daily_sigma = annual_vol / std::sqrt(252.0);
        double price = start_price;

        for (int i = 0; i < num_days; ++i) {
            double z_idio = norm(rng);
            double z_mkt = 0.0;

            // Market return component
            if (i > 0 && i < static_cast<int>(benchmark.size())) {
                z_mkt = (benchmark[i].adj_close / benchmark[i-1].adj_close - 1.0) /
                         (0.16 / std::sqrt(252.0));
            }

            double z = beta * z_mkt + std::sqrt(1.0 - beta * beta * 0.5) * z_idio;
            if (std::abs(z) > 2.5) z *= 1.3;

            double ret = daily_mu + daily_sigma * z;
            double new_price = price * std::exp(ret);

            double intraday_vol = std::abs(daily_sigma * norm(rng));
            double high = new_price * (1.0 + intraday_vol);
            double low = new_price * (1.0 - intraday_vol);
            double open = price + (new_price - price) * (0.3 + 0.4 * (rng() % 100) / 100.0);
            double vol = base_volume * (0.5 + 1.5 * (rng() % 100) / 100.0);

            int64_t ts = (i < static_cast<int>(benchmark.size())) ? benchmark[i].timestamp : 946684800 + i * 86400;
            bars.push_back({ts, open, high, low, new_price, vol, new_price});
            price = new_price;
        }

        return bars;
    }
};

} // namespace bt
