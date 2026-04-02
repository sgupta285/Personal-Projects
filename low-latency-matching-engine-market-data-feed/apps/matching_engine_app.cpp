#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

#include "llmde/engine/matching_engine.hpp"

namespace {
llmde::core::Side parse_side(const std::string& side) {
    return (side == "B" || side == "BUY") ? llmde::core::Side::Buy : llmde::core::Side::Sell;
}
}

int main(int argc, char** argv) {
    const std::string input_path = argc > 1 ? argv[1] : "data/orders.csv";
    llmde::engine::MatchingEngine engine("AAPL");

    std::ifstream file(input_path);
    if (!file) {
        std::cerr << "Unable to open input file: " << input_path << '\n';
        return 1;
    }

    std::string line;
    std::getline(file, line);  // header

    using clock = std::chrono::steady_clock;
    std::uint64_t sequence = 1;
    std::size_t processed = 0;
    std::size_t executions_before = 0;
    const auto started = clock::now();

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }
        std::stringstream ss(line);
        std::string action;
        std::getline(ss, action, ',');

        if (action == "ADD") {
            std::string side;
            std::string id;
            std::string price;
            std::string qty;
            std::getline(ss, id, ',');
            std::getline(ss, side, ',');
            std::getline(ss, price, ',');
            std::getline(ss, qty, ',');

            llmde::core::Order order{};
            order.id = std::stoull(id);
            order.side = parse_side(side);
            order.price = std::stoll(price);
            order.quantity = std::stoll(qty);
            order.sequence = sequence++;
            engine.submit(order);
        } else if (action == "CANCEL") {
            std::string id;
            std::getline(ss, id, ',');
            engine.cancel(std::stoull(id));
        }
        ++processed;
    }

    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(clock::now() - started).count();
    const auto snapshot = engine.snapshot();
    const auto executions = engine.recent_executions().size();
    std::cout << "processed=" << processed
              << " elapsed_us=" << elapsed
              << " throughput_orders_per_sec=" << std::fixed << std::setprecision(2)
              << (elapsed == 0 ? 0.0 : (static_cast<double>(processed) * 1000000.0 / static_cast<double>(elapsed)))
              << " executions_seen=" << (executions - executions_before) << '\n';
    std::cout << "best_bid=" << snapshot.best_bid << " best_bid_qty=" << snapshot.best_bid_qty
              << " best_ask=" << snapshot.best_ask << " best_ask_qty=" << snapshot.best_ask_qty << '\n';
    return 0;
}
