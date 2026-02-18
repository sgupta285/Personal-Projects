#pragma once

#include <string>
#include <cmath>
#include <vector>

namespace opt {

enum class OptionType { CALL, PUT };
enum class ExerciseStyle { EUROPEAN, AMERICAN };

struct OptionParams {
    double S;       // Spot price
    double K;       // Strike price
    double T;       // Time to expiry (years)
    double r;       // Risk-free rate
    double sigma;   // Volatility
    double q;       // Dividend yield (continuous)
    OptionType type;
    ExerciseStyle style = ExerciseStyle::EUROPEAN;
};

struct PricingResult {
    double price;
    double std_error;    // MC standard error (0 for analytical)
    double elapsed_ms;
    std::string method;
    int paths;           // MC paths used (0 for analytical)
};

struct Greeks {
    double delta;     // dV/dS
    double gamma;     // d²V/dS²
    double theta;     // dV/dT (per day)
    double vega;      // dV/dσ (per 1% vol move)
    double rho;       // dV/dr (per 1% rate move)
    double vanna;     // d²V/(dS dσ)
    double volga;     // d²V/dσ² (vomma)
    double charm;     // d²V/(dS dT) — delta decay
    double speed;     // d³V/dS³
    double elapsed_ms;
    std::string method;
};

struct VolSurfacePoint {
    double strike;
    double expiry;
    double implied_vol;
    double market_price;
    double model_price;
    double error;
};

struct CalibrationResult {
    std::vector<VolSurfacePoint> surface;
    double total_rmse;
    double max_error;
    double elapsed_ms;
    int iterations;
};

// Convenience
inline double intrinsic_value(double S, double K, OptionType type) {
    return (type == OptionType::CALL) ? std::max(S - K, 0.0) : std::max(K - S, 0.0);
}

inline double moneyness(double S, double K) {
    return (K > 0.0) ? S / K : 0.0;
}

inline const char* type_str(OptionType t) {
    return (t == OptionType::CALL) ? "Call" : "Put";
}

} // namespace opt
