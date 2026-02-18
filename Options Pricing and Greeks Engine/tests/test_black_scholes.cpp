#include "test_framework.h"
#include "pricing/black_scholes.h"
#include "pricing/types.h"
#include <cmath>

using namespace opt;

TEST(bs_call_atm) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    auto r = BlackScholes::price(p);
    // ATM call with these params should be ~$10.45
    ASSERT_GT(r.price, 9.0);
    ASSERT_LT(r.price, 12.0);
}

TEST(bs_put_atm) {
    OptionParams p{100, 100, 1.0, 0.05, 0.20, 0.0, OptionType::PUT};
    auto r = BlackScholes::price(p);
    ASSERT_GT(r.price, 4.0);
    ASSERT_LT(r.price, 8.0);
}

TEST(bs_put_call_parity) {
    double S = 100, K = 105, T = 0.5, r = 0.05, sigma = 0.25, q = 0.02;
    OptionParams call{S, K, T, r, sigma, q, OptionType::CALL};
    OptionParams put{S, K, T, r, sigma, q, OptionType::PUT};

    double c = BlackScholes::price(call).price;
    double p = BlackScholes::price(put).price;
    double parity = c - p;
    double expected = S * std::exp(-q * T) - K * std::exp(-r * T);
    ASSERT_NEAR(parity, expected, 1e-8);
}

TEST(bs_deep_itm_call) {
    OptionParams p{200, 100, 1.0, 0.05, 0.20, 0.0, OptionType::CALL};
    auto r = BlackScholes::price(p);
    // Deep ITM call ≈ S - K*exp(-rT) = 200 - 95.12 ≈ 104.88
    ASSERT_GT(r.price, 100.0);
    ASSERT_LT(r.price, 110.0);
}

TEST(bs_deep_otm_put) {
    OptionParams p{200, 100, 1.0, 0.05, 0.20, 0.0, OptionType::PUT};
    auto r = BlackScholes::price(p);
    // Deep OTM put ≈ 0
    ASSERT_LT(r.price, 0.01);
}

TEST(bs_zero_vol) {
    // With zero vol, call = max(S*e^(-qT) - K*e^(-rT), 0)
    OptionParams p{100, 95, 1.0, 0.05, 0.001, 0.0, OptionType::CALL};
    auto r = BlackScholes::price(p);
    double expected = 100 - 95 * std::exp(-0.05);
    ASSERT_NEAR(r.price, expected, 0.5); // Approx due to tiny vol
}

TEST(bs_increasing_vol_increases_price) {
    OptionParams low{100, 100, 1.0, 0.05, 0.10, 0.0, OptionType::CALL};
    OptionParams high{100, 100, 1.0, 0.05, 0.40, 0.0, OptionType::CALL};
    ASSERT_GT(BlackScholes::price(high).price, BlackScholes::price(low).price);
}
