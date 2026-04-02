#include <cstdlib>
#include <iostream>
#include <variant>

#include "llmde/feed/itch_parser.hpp"

namespace {
void expect(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}
}  // namespace

int main() {
    using namespace llmde;

    core::Order order{};
    order.id = 42;
    order.side = core::Side::Sell;
    order.price = 12345;
    order.quantity = 75;

    const auto add_bytes = feed::ItchParser::encode_add(order);
    const auto parsed_add = feed::ItchParser::parse(std::span<const std::byte>(add_bytes.data(), add_bytes.size()));
    expect(parsed_add.has_value(), "parsed add message");
    expect(std::holds_alternative<feed::AddOrderMessage>(*parsed_add), "add message variant");
    auto add_msg = std::get<feed::AddOrderMessage>(*parsed_add);
    expect(add_msg.order.id == 42, "add order id");
    expect(add_msg.order.side == core::Side::Sell, "add side");

    const auto cancel_bytes = feed::ItchParser::encode_cancel(42);
    const auto parsed_cancel = feed::ItchParser::parse(std::span<const std::byte>(cancel_bytes.data(), cancel_bytes.size()));
    expect(parsed_cancel.has_value(), "parsed cancel message");
    expect(std::holds_alternative<feed::CancelOrderMessage>(*parsed_cancel), "cancel message variant");

    std::cout << "parser_tests passed\n";
    return 0;
}
