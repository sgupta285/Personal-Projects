#include "test_framework.h"
#include "calibration/vol_surface.h"

using namespace opt;

TEST(vol_surface_calibration_low_rmse) {
    std::vector<double> strikes = {90, 95, 100, 105, 110};
    std::vector<double> expiries = {0.25, 0.50, 1.00};
    auto quotes = VolSurface::generate_market_quotes(100, 0.05, strikes, expiries);
    auto result = VolSurface::calibrate(quotes, 100, 0.05);

    // RMSE should be essentially zero (we generated from BS, calibrating back)
    ASSERT_LT(result.total_rmse, 0.01);
    ASSERT_LT(result.max_error, 0.01);
}

TEST(vol_surface_smile_shape) {
    std::vector<double> strikes = {80, 90, 100, 110, 120};
    std::vector<double> expiries = {1.0};
    auto quotes = VolSurface::generate_market_quotes(100, 0.05, strikes, expiries, 0.20, -0.10, 0.05);
    auto result = VolSurface::calibrate(quotes, 100, 0.05);

    // OTM puts (low strike) should have higher IV than ATM
    double iv_80 = 0, iv_100 = 0;
    for (const auto& pt : result.surface) {
        if (std::abs(pt.strike - 80) < 0.01) iv_80 = pt.implied_vol;
        if (std::abs(pt.strike - 100) < 0.01) iv_100 = pt.implied_vol;
    }
    ASSERT_GT(iv_80, iv_100); // Skew present
}

TEST(vol_surface_all_vols_positive) {
    std::vector<double> strikes = {85, 90, 95, 100, 105, 110, 115};
    std::vector<double> expiries = {0.08, 0.25, 0.50, 1.00};
    auto quotes = VolSurface::generate_market_quotes(100, 0.05, strikes, expiries);
    auto result = VolSurface::calibrate(quotes, 100, 0.05);

    for (const auto& pt : result.surface) {
        ASSERT_GT(pt.implied_vol, 0.0);
        ASSERT_LT(pt.implied_vol, 5.0);
    }
}
