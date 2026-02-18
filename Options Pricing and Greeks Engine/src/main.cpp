/**
 * Options Pricing & Greeks Engine
 * Demonstrates Black-Scholes, Monte Carlo, Greeks, and vol surface calibration.
 *
 * Usage: ./options_pricer [--mc-paths N] [--spot S] [--strike K] [--vol V]
 */

#include "pricing/black_scholes.h"
#include "pricing/binomial_tree.h"
#include "monte_carlo/mc_engine.h"
#include "greeks/finite_difference.h"
#include "calibration/implied_vol.h"
#include "calibration/vol_surface.h"
#include "utils/timer.h"

#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>

using namespace opt;

void print_divider(const std::string& title) {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "  " << title << "\n";
    std::cout << std::string(70, '=') << "\n\n";
}

int main(int argc, char* argv[]) {
    // Default parameters
    double S = 100.0, K = 100.0, T = 1.0, r = 0.05, sigma = 0.20, q = 0.02;
    int mc_paths = 10000;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--spot" && i+1 < argc) S = std::stod(argv[++i]);
        else if (arg == "--strike" && i+1 < argc) K = std::stod(argv[++i]);
        else if (arg == "--vol" && i+1 < argc) sigma = std::stod(argv[++i]);
        else if (arg == "--rate" && i+1 < argc) r = std::stod(argv[++i]);
        else if (arg == "--expiry" && i+1 < argc) T = std::stod(argv[++i]);
        else if (arg == "--mc-paths" && i+1 < argc) mc_paths = std::stoi(argv[++i]);
    }

    OptionParams call{S, K, T, r, sigma, q, OptionType::CALL};
    OptionParams put{S, K, T, r, sigma, q, OptionType::PUT};

    std::cout << std::string(70, '=') << "\n";
    std::cout << "  OPTIONS PRICING & GREEKS ENGINE\n";
    std::cout << std::string(70, '=') << "\n";
    std::cout << "  Spot=" << S << "  Strike=" << K << "  T=" << T
              << "  r=" << r*100 << "%  σ=" << sigma*100 << "%  q=" << q*100 << "%\n";

    // ========================================
    // 1. PRICING COMPARISON
    // ========================================
    print_divider("1. PRICING COMPARISON");

    auto bs_call = BlackScholes::price(call);
    auto bs_put = BlackScholes::price(put);
    std::cout << "Black-Scholes:\n";
    std::cout << "  Call: $" << std::fixed << std::setprecision(4) << bs_call.price
              << "  (" << std::setprecision(3) << bs_call.elapsed_ms << " ms)\n";
    std::cout << "  Put:  $" << std::setprecision(4) << bs_put.price
              << "  (" << std::setprecision(3) << bs_put.elapsed_ms << " ms)\n";

    // Verify put-call parity: C - P = S*e^(-qT) - K*e^(-rT)
    double parity = bs_call.price - bs_put.price;
    double expected_parity = S * std::exp(-q * T) - K * std::exp(-r * T);
    std::cout << "  Put-Call Parity Error: " << std::scientific << std::setprecision(2)
              << std::abs(parity - expected_parity) << "\n\n";

    // Monte Carlo with different variance reduction
    struct MCConfig { VarianceReduction vr; std::string name; };
    std::vector<MCConfig> mc_configs = {
        {VarianceReduction::NONE, "Standard"},
        {VarianceReduction::ANTITHETIC, "Antithetic"},
        {VarianceReduction::STRATIFIED, "Stratified"},
        {VarianceReduction::CONTROL_VARIATE, "Control Variate"},
    };

    std::cout << "Monte Carlo (" << mc_paths << " paths):\n";
    for (const auto& cfg : mc_configs) {
        auto mc_call = MonteCarloEngine::price(call, mc_paths, cfg.vr);
        double err_pct = std::abs(mc_call.price - bs_call.price) / bs_call.price * 100;
        std::cout << std::fixed << "  " << std::setw(16) << std::left << cfg.name
                  << " Call=$" << std::setprecision(4) << mc_call.price
                  << "  SE=$" << std::setprecision(4) << mc_call.std_error
                  << "  Err=" << std::setprecision(2) << err_pct << "%"
                  << "  (" << std::setprecision(1) << mc_call.elapsed_ms << " ms)\n";
    }

    // Binomial tree
    for (int steps : {100, 500, 1000}) {
        auto bt_call = BinomialTree::price(call, steps);
        double err_pct = std::abs(bt_call.price - bs_call.price) / bs_call.price * 100;
        std::cout << "\nBinomial Tree (" << steps << " steps):\n"
                  << "  Call=$" << std::setprecision(4) << bt_call.price
                  << "  Err=" << std::setprecision(4) << err_pct << "%"
                  << "  (" << std::setprecision(1) << bt_call.elapsed_ms << " ms)\n";
    }

    // American option (binomial only)
    OptionParams am_put = put;
    am_put.style = ExerciseStyle::AMERICAN;
    auto am_result = BinomialTree::price(am_put, 500);
    std::cout << "\nAmerican Put (Binomial 500): $" << std::setprecision(4) << am_result.price
              << " (European: $" << bs_put.price << ", early exercise premium: $"
              << am_result.price - bs_put.price << ")\n";

    // ========================================
    // 2. GREEKS
    // ========================================
    print_divider("2. GREEKS COMPARISON");

    auto analytical = BlackScholes::all_greeks(call);
    auto fd = FiniteDifferenceGreeks::compute(call);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << std::setw(12) << "Greek" << std::setw(15) << "Analytical" << std::setw(15) << "Finite Diff"
              << std::setw(15) << "Error (%)" << "\n";
    std::cout << std::string(57, '-') << "\n";

    auto print_greek = [](const char* name, double a, double fd) {
        double err = (std::abs(a) > 1e-10) ? std::abs((fd - a) / a) * 100 : std::abs(fd - a);
        std::cout << std::setw(12) << name << std::setw(15) << a << std::setw(15) << fd
                  << std::setw(14) << std::setprecision(4) << err << "%\n";
    };

    print_greek("Delta", analytical.delta, fd.delta);
    print_greek("Gamma", analytical.gamma, fd.gamma);
    print_greek("Theta", analytical.theta, fd.theta);
    print_greek("Vega", analytical.vega, fd.vega);
    print_greek("Rho", analytical.rho, fd.rho);
    print_greek("Vanna", analytical.vanna, fd.vanna);
    print_greek("Volga", analytical.volga, fd.volga);

    std::cout << "\nAnalytical: " << analytical.elapsed_ms << " ms  |  Finite Diff: " << fd.elapsed_ms << " ms\n";

    // ========================================
    // 3. IMPLIED VOLATILITY
    // ========================================
    print_divider("3. IMPLIED VOLATILITY");

    double test_price = bs_call.price;
    double recovered_vol = ImpliedVolSolver::solve(test_price, S, K, T, r, q, OptionType::CALL);
    std::cout << "Input vol:     " << std::setprecision(6) << sigma << "\n";
    std::cout << "Market price:  $" << test_price << "\n";
    std::cout << "Recovered vol: " << recovered_vol << "\n";
    std::cout << "Error:         " << std::scientific << std::abs(recovered_vol - sigma) << "\n";

    // ========================================
    // 4. VOLATILITY SURFACE CALIBRATION
    // ========================================
    print_divider("4. VOLATILITY SURFACE CALIBRATION");

    std::vector<double> strikes = {80, 85, 90, 95, 100, 105, 110, 115, 120};
    std::vector<double> expiries = {0.08, 0.25, 0.50, 1.00, 2.00};

    auto quotes = VolSurface::generate_market_quotes(S, r, strikes, expiries, 0.20, -0.10, 0.05);
    std::cout << "Market quotes: " << quotes.size() << " (9 strikes x 5 expiries)\n";

    auto cal = VolSurface::calibrate(quotes, S, r, q);
    VolSurface::print_surface(cal, strikes, expiries, S);

    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "  ENGINE COMPLETE\n";
    std::cout << std::string(70, '=') << "\n";

    return 0;
}
