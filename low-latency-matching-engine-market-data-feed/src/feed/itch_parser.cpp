#include "llmde/feed/itch_parser.hpp"

#include <cstring>

namespace llmde::feed {
namespace {
#pragma pack(push, 1)
struct AddWireMessage {
    char type;
    std::uint64_t order_id;
    char side;
    std::int64_t price;
    std::int64_t quantity;
};

struct CancelWireMessage {
    char type;
    std::uint64_t order_id;
};
#pragma pack(pop)
}  // namespace

std::optional<FeedMessage> ItchParser::parse(std::span<const std::byte> bytes) {
    if (bytes.empty()) {
        return std::nullopt;
    }
    const auto* raw = reinterpret_cast<const char*>(bytes.data());
    if (raw[0] == 'A' && bytes.size() >= sizeof(AddWireMessage)) {
        AddWireMessage msg{};
        std::memcpy(&msg, bytes.data(), sizeof(msg));
        core::Order order{};
        order.id = msg.order_id;
        order.side = msg.side == 'B' ? core::Side::Buy : core::Side::Sell;
        order.price = msg.price;
        order.quantity = msg.quantity;
        order.type = core::OrderType::Limit;
        return AddOrderMessage{order};
    }
    if (raw[0] == 'C' && bytes.size() >= sizeof(CancelWireMessage)) {
        CancelWireMessage msg{};
        std::memcpy(&msg, bytes.data(), sizeof(msg));
        return CancelOrderMessage{msg.order_id};
    }
    return std::nullopt;
}

std::vector<std::byte> ItchParser::encode_add(const core::Order& order) {
    AddWireMessage msg{};
    msg.type = 'A';
    msg.order_id = order.id;
    msg.side = order.side == core::Side::Buy ? 'B' : 'S';
    msg.price = order.price;
    msg.quantity = order.quantity;
    std::vector<std::byte> bytes(sizeof(msg));
    std::memcpy(bytes.data(), &msg, sizeof(msg));
    return bytes;
}

std::vector<std::byte> ItchParser::encode_cancel(std::uint64_t order_id) {
    CancelWireMessage msg{};
    msg.type = 'C';
    msg.order_id = order_id;
    std::vector<std::byte> bytes(sizeof(msg));
    std::memcpy(bytes.data(), &msg, sizeof(msg));
    return bytes;
}

}  // namespace llmde::feed
