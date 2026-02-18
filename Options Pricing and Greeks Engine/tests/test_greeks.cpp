#include "test_framework.h"
#include "pricing/black_scholes.h"
#include "greeks/finite_difference.h"

using namespace opt;

TEST(greeks_delta_call_bounds) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double d = BlackScholes::delta(p);
    ASSERT_GT(d, 0.0);
    ASSERT_LT(d, 1.0);
}

TEST(greeks_delta_put_bounds) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::PUT};
    double d = BlackScholes::delta(p);
    ASSERT_GT(d, -1.0);
    ASSERT_LT(d, 0.0);
}

TEST(greeks_gamma_positive) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    ASSERT_GT(BlackScholes::gamma(p), 0.0);
}

TEST(greeks_vega_positive) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    ASSERT_GT(BlackScholes::vega(p), 0.0);
}

TEST(greeks_fd_matches_analytical_delta) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double a = BlackScholes::delta(p);
    auto fd = FiniteDifferenceGreeks::compute(p);
    double err = std::abs(fd.delta - a) / std::abs(a);
    ASSERT_LT(err, 0.001); // <0.1% error
}

TEST(greeks_fd_matches_analytical_gamma) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double a = BlackScholes::gamma(p);
    auto fd = FiniteDifferenceGreeks::compute(p);
    double err = std::abs(fd.gamma - a) / std::abs(a);
    ASSERT_LT(err, 0.01); // <1% error
}

TEST(greeks_fd_matches_analytical_vega) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    double a = BlackScholes::vega(p);
    auto fd = FiniteDifferenceGreeks::compute(p);
    double err = std::abs(fd.vega - a) / std::abs(a);
    ASSERT_LT(err, 0.001);
}

TEST(greeks_theta_call_negative) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    // Theta should be negative for a plain vanilla call (time decay)
    double theta = BlackScholes::theta(p);
    ASSERT_LT(theta, 0.0);
}
