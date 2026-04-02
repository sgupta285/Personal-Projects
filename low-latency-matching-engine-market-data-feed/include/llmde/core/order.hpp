#pragma once

#include <cstdint>
#include <string>

namespace llmde::core {

enum class Side : std::uint8_t {
    Buy = 0,
    Sell = 1,
};

enum class OrderType : std::uint8_t {
    Limit = 0,
    Market = 1,
};

struct Order {
    std::uint64_t id{};
    std::string symbol{"AAPL"};
    Side side{Side::Buy};
    OrderType type{OrderType::Limit};
    std::int64_t price{};    // price in cents
    std::int64_t quantity{};
    std::uint64_t sequence{};
};

struct Execution {
    std::uint64_t resting_order_id{};
    std::uint64_t aggressive_order_id{};
    std::int64_t price{};
    std::int64_t quantity{};
};

struct BookSnapshot {
    std::int64_t best_bid{};
    std::int64_t best_bid_qty{};
    std::int64_t best_ask{};
    std::int64_t best_ask_qty{};
};

}  // namespace llmde::core
