#pragma once

#include "pricing/types.h"
#include "calibration/implied_vol.h"
#include <vector>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <iostream>
#include <iomanip>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace opt {

struct MarketQuote {
    double strike;
    double expiry;    // years
    double market_price;
    OptionType type;
};

class VolSurface {
public:
    // Calibrate implied vol surface from market quotes
    static CalibrationResult calibrate(
        const std::vector<MarketQuote>& quotes,
        double spot, double rate, double div_yield = 0.0
    ) {
        auto t0 = std::chrono::high_resolution_clock::now();

        CalibrationResult result;
        result.surface.resize(quotes.size());
        result.total_rmse = 0.0;
        result.max_error = 0.0;

        #pragma omp parallel for schedule(dynamic)
        for (size_t i = 0; i < quotes.size(); ++i) {
            const auto& q = quotes[i];

            double iv = ImpliedVolSolver::solve(
                q.market_price, spot, q.strike, q.expiry, rate, div_yield, q.type
            );

            OptionParams p{spot, q.strike, q.expiry, rate, iv, div_yield, q.type};
            double model_price = BlackScholes::price(p).price;
            double error = std::abs(model_price - q.market_price);

            result.surface[i] = {
                q.strike, q.expiry, iv,
                q.market_price, model_price, error
            };
        }

        // Compute aggregate stats
        double sse = 0.0;
        for (const auto& pt : result.surface) {
            sse += pt.error * pt.error;
            result.max_error = std::max(result.max_error, pt.error);
        }
        result.total_rmse = std::sqrt(sse / result.surface.size());

        auto t1 = std::chrono::high_resolution_clock::now();
        result.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
        result.iterations = static_cast<int>(quotes.size());

        return result;
    }

    // Generate synthetic market quotes with vol smile
    static std::vector<MarketQuote> generate_market_quotes(
        double spot, double rate,
        const std::vector<double>& strikes,
        const std::vector<double>& expiries,
        double base_vol = 0.20,
        double skew = -0.10,     // Vol skew per unit log-moneyness
        double smile = 0.05      // Vol smile curvature
    ) {
        std::vector<MarketQuote> quotes;

        for (double T : expiries) {
            for (double K : strikes) {
                double m = std::log(K / spot); // Log moneyness
                double term_adj = std::sqrt(0.5 / T); // Term structure flattening

                // SVI-like vol parameterization
                double vol = base_vol + skew * m * term_adj + smile * m * m;
                vol = std::max(vol, 0.05);

                OptionType type = (K >= spot) ? OptionType::CALL : OptionType::PUT;
                OptionParams p{spot, K, T, rate, vol, 0.0, type};
                double price = BlackScholes::price(p).price;

                quotes.push_back({K, T, price, type});
            }
        }

        return quotes;
    }

    // Print vol surface as a grid
    static void print_surface(const CalibrationResult& result,
                               const std::vector<double>& strikes,
                               const std::vector<double>& expiries,
                               double spot) {
        std::cout << "\nImplied Volatility Surface:\n";
        std::cout << std::setw(10) << "K/S\\T";
        for (double T : expiries) {
            std::cout << std::setw(10) << std::fixed << std::setprecision(2) << T;
        }
        std::cout << "\n" << std::string(10 + expiries.size() * 10, '-') << "\n";

        for (double K : strikes) {
            std::cout << std::setw(9) << std::setprecision(0) << K << " ";
            for (double T : expiries) {
                // Find matching surface point
                double iv = 0.0;
                for (const auto& pt : result.surface) {
                    if (std::abs(pt.strike - K) < 0.01 && std::abs(pt.expiry - T) < 0.001) {
                        iv = pt.implied_vol;
                        break;
                    }
                }
                std::cout << std::setw(9) << std::setprecision(2) << (iv * 100) << "%";
            }
            std::cout << "\n";
        }

        std::cout << "\nCalibration RMSE: " << std::setprecision(6) << result.total_rmse;
        std::cout << "  Max Error: " << result.max_error;
        std::cout << "  Time: " << std::setprecision(1) << result.elapsed_ms << " ms\n";
    }
};

} // namespace opt
