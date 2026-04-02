#include <fstream>
#include <iostream>
#include <vector>

#include "llmde/engine/matching_engine.hpp"
#include "llmde/feed/itch_parser.hpp"

int main(int argc, char** argv) {
    const std::string input_path = argc > 1 ? argv[1] : "data/itch_feed.bin";
    std::ifstream file(input_path, std::ios::binary);
    if (!file) {
        std::cerr << "Unable to open feed file: " << input_path << '\n';
        return 1;
    }

    llmde::engine::MatchingEngine engine("AAPL");
    std::vector<char> bytes((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());

    std::size_t offset = 0;
    while (offset < bytes.size()) {
        const char type = bytes[offset];
        std::size_t size = 0;
        if (type == 'A') {
            size = 1 + sizeof(std::uint64_t) + 1 + sizeof(std::int64_t) + sizeof(std::int64_t);
        } else if (type == 'C') {
            size = 1 + sizeof(std::uint64_t);
        } else {
            std::cerr << "Unknown message type in feed: " << type << '\n';
            return 2;
        }

        auto* begin = reinterpret_cast<const std::byte*>(bytes.data() + static_cast<std::ptrdiff_t>(offset));
        auto parsed = llmde::feed::ItchParser::parse(std::span<const std::byte>(begin, size));
        if (parsed) {
            std::visit(
                [&](const auto& message) {
                    using T = std::decay_t<decltype(message)>;
                    if constexpr (std::is_same_v<T, llmde::feed::AddOrderMessage>) {
                        engine.submit(message.order);
                    } else if constexpr (std::is_same_v<T, llmde::feed::CancelOrderMessage>) {
                        engine.cancel(message.order_id);
                    }
                },
                *parsed);
        }
        offset += size;
    }

    const auto snapshot = engine.snapshot();
    std::cout << "feed replay complete best_bid=" << snapshot.best_bid << " best_ask=" << snapshot.best_ask << '\n';
    return 0;
}
