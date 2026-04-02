#include "bef/cost_model.hpp"

#include <chrono>
#include <iostream>

int main() {
    constexpr int iterations = 500000;
    bef::CostInput input{
        .mid_price = 101.25,
        .quantity = 250.0,
        .spread_bps = 4.0,
        .volatility_bps = 22.0,
        .participation_rate = 0.08,
        .commission_per_share = 0.0035,
        .route_fee_bps = 0.5,
        .latency_ms = 8.0,
    };

    volatile double sink = 0.0;
    const auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < iterations; ++i) {
        const auto tier = static_cast<bef::ExecutionTier>(i % 6);
        sink += bef::fill_price(tier, input, i % 2 == 0);
    }
    const auto end = std::chrono::steady_clock::now();
    const auto elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();

    std::cout << "iterations=" << iterations << "\n";
    std::cout << "elapsed_ns=" << elapsed_ns << "\n";
    std::cout << "ns_per_fill=" << static_cast<double>(elapsed_ns) / iterations << "\n";
    std::cout << "guard=" << sink << "\n";
    return 0;
}
