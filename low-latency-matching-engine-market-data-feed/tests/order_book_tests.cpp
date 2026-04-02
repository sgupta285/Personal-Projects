#include <cstdlib>
#include <iostream>
#include <vector>

#include "llmde/core/order_book.hpp"

namespace {
void expect(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}
}  // namespace

int main() {
    using namespace llmde::core;

    OrderBook book;
    std::vector<Execution> executions;

    expect(book.add(Order{1, "AAPL", Side::Buy, OrderType::Limit, 10000, 50, 1}, [&](const Execution& e) { executions.push_back(e); }), "add buy");
    expect(book.add(Order{2, "AAPL", Side::Sell, OrderType::Limit, 10100, 25, 2}, [&](const Execution& e) { executions.push_back(e); }), "add sell");

    auto snap = book.snapshot().value();
    expect(snap.best_bid == 10000, "best bid before cross");
    expect(snap.best_ask == 10100, "best ask before cross");

    expect(book.add(Order{3, "AAPL", Side::Buy, OrderType::Limit, 10100, 10, 3}, [&](const Execution& e) { executions.push_back(e); }), "crossing buy");
    expect(executions.size() == 1, "one execution produced");
    expect(executions.front().quantity == 10, "execution quantity");
    snap = book.snapshot().value();
    expect(snap.best_ask_qty == 15, "ask quantity reduced");

    expect(book.cancel(1), "cancel existing order");
    snap = book.snapshot().value();
    expect(snap.best_bid == 0, "bid cleared after cancel");

    std::cout << "order_book_tests passed\n";
    return 0;
}
