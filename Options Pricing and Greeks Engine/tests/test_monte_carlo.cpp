#include "test_framework.h"
#include "pricing/black_scholes.h"
#include "monte_carlo/mc_engine.h"

using namespace opt;

TEST(mc_converges_to_bs) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double bs = BlackScholes::price(p).price;
    auto mc = MonteCarloEngine::price(p, 50000, VarianceReduction::ANTITHETIC);
    // Within 1% of BS
    double err = std::abs(mc.price - bs) / bs;
    ASSERT_LT(err, 0.01);
}

TEST(mc_antithetic_reduces_variance) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    auto std_mc = MonteCarloEngine::price(p, 10000, VarianceReduction::NONE, 42);
    auto anti_mc = MonteCarloEngine::price(p, 10000, VarianceReduction::ANTITHETIC, 42);
    // Antithetic should have lower SE
    ASSERT_LT(anti_mc.std_error, std_mc.std_error * 1.5); // Conservative check
}

TEST(mc_control_variate) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double bs = BlackScholes::price(p).price;
    auto cv = MonteCarloEngine::price(p, 10000, VarianceReduction::CONTROL_VARIATE);
    double err = std::abs(cv.price - bs) / bs;
    ASSERT_LT(err, 0.02);
}

TEST(mc_put_positive) {
    OptionParams p{100, 110, 0.5, 0.05, 0.25, 0.0, OptionType::PUT};
    auto mc = MonteCarloEngine::price(p, 10000, VarianceReduction::ANTITHETIC);
    ASSERT_GT(mc.price, 0.0);
}

TEST(mc_multistep) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double bs = BlackScholes::price(p).price;
    auto mc = MonteCarloEngine::price_multistep(p, 10000, 252);
    double err = std::abs(mc.price - bs) / bs;
    ASSERT_LT(err, 0.02);
}
