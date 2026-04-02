#include "llmde/engine/matching_engine.hpp"

#include <sstream>

namespace llmde::engine {

MatchingEngine::MatchingEngine(std::string symbol, std::string market_data_host, std::uint16_t market_data_port)
    : symbol_(std::move(symbol)), publisher_(std::move(market_data_host), market_data_port) {}

bool MatchingEngine::submit(core::Order order) {
    if (order.symbol.empty()) {
        order.symbol = symbol_;
    }
    const bool ok = book_.add(order, [this](const core::Execution& execution) {
        recent_executions_.push_back(execution);
        if (recent_executions_.size() > 1024) {
            recent_executions_.erase(recent_executions_.begin(), recent_executions_.begin() + 256);
        }
        publish_execution(execution);
    });
    publish_snapshot();
    return ok;
}

bool MatchingEngine::cancel(std::uint64_t order_id) {
    const bool ok = book_.cancel(order_id);
    publish_snapshot();
    return ok;
}

core::BookSnapshot MatchingEngine::snapshot() const {
    return book_.snapshot().value_or(core::BookSnapshot{});
}

const std::vector<core::Execution>& MatchingEngine::recent_executions() const noexcept {
    return recent_executions_;
}

void MatchingEngine::publish_execution(const core::Execution& execution) {
    std::ostringstream out;
    out << "EXEC|symbol=" << symbol_
        << "|resting=" << execution.resting_order_id
        << "|aggr=" << execution.aggressive_order_id
        << "|price=" << execution.price
        << "|qty=" << execution.quantity;
    publisher_.publish(out.str());
}

void MatchingEngine::publish_snapshot() {
    const auto snap = snapshot();
    std::ostringstream out;
    out << "BOOK|symbol=" << symbol_
        << "|best_bid=" << snap.best_bid
        << "|best_bid_qty=" << snap.best_bid_qty
        << "|best_ask=" << snap.best_ask
        << "|best_ask_qty=" << snap.best_ask_qty;
    publisher_.publish(out.str());
}

}  // namespace llmde::engine
