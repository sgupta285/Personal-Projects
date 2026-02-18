#pragma once

#include "pricing/types.h"
#include "pricing/black_scholes.h"
#include <cmath>
#include <chrono>
#include <functional>

namespace opt {

class FiniteDifferenceGreeks {
public:
    // Compute all Greeks via central finite differences
    static Greeks compute(const OptionParams& p,
                          std::function<double(const OptionParams&)> pricer = nullptr)
    {
        auto t0 = std::chrono::high_resolution_clock::now();

        if (!pricer) {
            pricer = [](const OptionParams& params) { return BlackScholes::price(params).price; };
        }

        Greeks g;
        double base_price = pricer(p);

        // Delta: dV/dS
        double dS = p.S * 0.01;
        g.delta = central_diff(p, pricer, [&](OptionParams& pp, double h) { pp.S += h; }, dS);

        // Gamma: d²V/dS²
        g.gamma = second_diff(p, pricer, [&](OptionParams& pp, double h) { pp.S += h; }, dS);

        // Theta: dV/dT (per calendar day)
        double dT = 1.0 / 365.0;
        g.theta = -central_diff(p, pricer, [&](OptionParams& pp, double h) { pp.T += h; }, dT);

        // Vega: dV/dσ per 1% vol change
        double dSig = 0.01;
        g.vega = central_diff(p, pricer, [&](OptionParams& pp, double h) { pp.sigma += h; }, dSig) / 100.0;

        // Rho: dV/dr per 1% rate change
        double dR = 0.01;
        g.rho = central_diff(p, pricer, [&](OptionParams& pp, double h) { pp.r += h; }, dR) / 100.0;

        // Vanna: d²V/(dS dσ)
        g.vanna = cross_diff(p, pricer,
            [](OptionParams& pp, double h) { pp.S += h; },
            [](OptionParams& pp, double h) { pp.sigma += h; },
            dS, dSig);

        // Volga: d²V/dσ²
        g.volga = second_diff(p, pricer, [](OptionParams& pp, double h) { pp.sigma += h; }, dSig);

        // Charm: d²V/(dS dT) — delta decay
        g.charm = cross_diff(p, pricer,
            [](OptionParams& pp, double h) { pp.S += h; },
            [](OptionParams& pp, double h) { pp.T += h; },
            dS, dT);

        // Speed: d³V/dS³
        g.speed = third_diff(p, pricer, [](OptionParams& pp, double h) { pp.S += h; }, dS);

        g.method = "Finite Difference";
        auto t1 = std::chrono::high_resolution_clock::now();
        g.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
        return g;
    }

private:
    using Perturb = std::function<void(OptionParams&, double)>;

    static double central_diff(const OptionParams& p,
                                std::function<double(const OptionParams&)>& pricer,
                                Perturb perturb, double h) {
        OptionParams up = p, down = p;
        perturb(up, h);
        perturb(down, -h);
        return (pricer(up) - pricer(down)) / (2.0 * h);
    }

    static double second_diff(const OptionParams& p,
                               std::function<double(const OptionParams&)>& pricer,
                               Perturb perturb, double h) {
        OptionParams up = p, down = p;
        perturb(up, h);
        perturb(down, -h);
        double base = pricer(p);
        return (pricer(up) - 2.0 * base + pricer(down)) / (h * h);
    }

    static double third_diff(const OptionParams& p,
                              std::function<double(const OptionParams&)>& pricer,
                              Perturb perturb, double h) {
        OptionParams p1 = p, p2 = p, m1 = p, m2 = p;
        perturb(p1, h); perturb(p2, 2.0 * h);
        perturb(m1, -h); perturb(m2, -2.0 * h);
        return (pricer(p2) - 2.0 * pricer(p1) + 2.0 * pricer(m1) - pricer(m2)) / (2.0 * h * h * h);
    }

    static double cross_diff(const OptionParams& p,
                              std::function<double(const OptionParams&)>& pricer,
                              Perturb perturb1, Perturb perturb2,
                              double h1, double h2) {
        OptionParams pp = p, pm = p, mp = p, mm = p;
        perturb1(pp, h1); perturb2(pp, h2);
        perturb1(pm, h1); perturb2(pm, -h2);
        perturb1(mp, -h1); perturb2(mp, h2);
        perturb1(mm, -h1); perturb2(mm, -h2);
        return (pricer(pp) - pricer(pm) - pricer(mp) + pricer(mm)) / (4.0 * h1 * h2);
    }
};

} // namespace opt
