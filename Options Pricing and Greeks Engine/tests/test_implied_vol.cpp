#include "test_framework.h"
#include "pricing/black_scholes.h"
#include "calibration/implied_vol.h"

using namespace opt;

TEST(iv_recovers_input_vol) {
    double sigma = 0.25;
    OptionParams p{100, 100, 1.0, 0.05, sigma, 0.0, OptionType::CALL};
    double price = BlackScholes::price(p).price;
    double iv = ImpliedVolSolver::solve(price, 100, 100, 1.0, 0.05, 0.0, OptionType::CALL);
    ASSERT_NEAR(iv, sigma, 1e-6);
}

TEST(iv_works_for_put) {
    double sigma = 0.30;
    OptionParams p{100, 110, 0.5, 0.05, sigma, 0.0, OptionType::PUT};
    double price = BlackScholes::price(p).price;
    double iv = ImpliedVolSolver::solve(price, 100, 110, 0.5, 0.05, 0.0, OptionType::PUT);
    ASSERT_NEAR(iv, sigma, 1e-6);
}

TEST(iv_deep_otm) {
    double sigma = 0.20;
    OptionParams p{100, 150, 0.25, 0.05, sigma, 0.0, OptionType::CALL};
    double price = BlackScholes::price(p).price;
    double iv = ImpliedVolSolver::solve(price, 100, 150, 0.25, 0.05, 0.0, OptionType::CALL);
    ASSERT_NEAR(iv, sigma, 1e-4);
}

TEST(iv_high_vol) {
    double sigma = 0.80;
    OptionParams p{100, 100, 1.0, 0.05, sigma, 0.0, OptionType::CALL};
    double price = BlackScholes::price(p).price;
    double iv = ImpliedVolSolver::solve(price, 100, 100, 1.0, 0.05, 0.0, OptionType::CALL);
    ASSERT_NEAR(iv, sigma, 1e-4);
}

TEST(iv_with_dividend) {
    double sigma = 0.22;
    OptionParams p{100, 95, 1.0, 0.05, sigma, 0.03, OptionType::CALL};
    double price = BlackScholes::price(p).price;
    double iv = ImpliedVolSolver::solve(price, 100, 95, 1.0, 0.05, 0.03, OptionType::CALL);
    ASSERT_NEAR(iv, sigma, 1e-5);
}
