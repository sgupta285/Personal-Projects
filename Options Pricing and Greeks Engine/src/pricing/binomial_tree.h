#pragma once

#include "pricing/types.h"
#include <vector>
#include <cmath>
#include <algorithm>
#include <chrono>

namespace opt {

class BinomialTree {
public:
    static PricingResult price(const OptionParams& p, int steps = 500) {
        auto t0 = std::chrono::high_resolution_clock::now();

        double dt = p.T / steps;
        double u = std::exp(p.sigma * std::sqrt(dt));
        double d = 1.0 / u;
        double df = std::exp(-p.r * dt);
        double prob = (std::exp((p.r - p.q) * dt) - d) / (u - d);

        // Build terminal payoffs
        std::vector<double> prices(steps + 1);
        for (int i = 0; i <= steps; ++i) {
            double spot = p.S * std::pow(u, steps - i) * std::pow(d, i);
            prices[i] = intrinsic_value(spot, p.K, p.type);
        }

        // Backward induction
        for (int step = steps - 1; step >= 0; --step) {
            for (int i = 0; i <= step; ++i) {
                double continuation = df * (prob * prices[i] + (1.0 - prob) * prices[i + 1]);

                if (p.style == ExerciseStyle::AMERICAN) {
                    double spot = p.S * std::pow(u, step - i) * std::pow(d, i);
                    double exercise = intrinsic_value(spot, p.K, p.type);
                    prices[i] = std::max(continuation, exercise);
                } else {
                    prices[i] = continuation;
                }
            }
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        return {prices[0], 0.0, ms, "Binomial-" + std::to_string(steps), 0};
    }
};

} // namespace opt
