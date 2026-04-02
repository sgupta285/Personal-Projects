#pragma once

#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <variant>
#include <vector>

#include "llmde/core/order.hpp"

namespace llmde::feed {

struct AddOrderMessage {
    core::Order order;
};

struct CancelOrderMessage {
    std::uint64_t order_id{};
};

using FeedMessage = std::variant<AddOrderMessage, CancelOrderMessage>;

class ItchParser {
  public:
    static std::optional<FeedMessage> parse(std::span<const std::byte> bytes);
    static std::vector<std::byte> encode_add(const core::Order& order);
    static std::vector<std::byte> encode_cancel(std::uint64_t order_id);
};

}  // namespace llmde::feed
