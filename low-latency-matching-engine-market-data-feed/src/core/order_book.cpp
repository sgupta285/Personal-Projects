#include "llmde/core/order_book.hpp"

#include <algorithm>
#include <limits>

namespace llmde::core {

std::int64_t OrderBook::level_quantity(const LevelQueue& queue) {
    std::int64_t total = 0;
    for (const auto& node : queue) {
        if (node && node->active && node->order.quantity > 0) {
            total += node->order.quantity;
        }
    }
    return total;
}

void OrderBook::sweep_inactive(LevelQueue& queue) {
    while (!queue.empty()) {
        const auto& front = queue.front();
        if (front && front->active && front->order.quantity > 0) {
            break;
        }
        queue.pop_front();
    }
}

void OrderBook::refresh_best_bid() {
    std::optional<std::int64_t> best;
    for (auto& [price, queue] : bids_) {
        sweep_inactive(queue);
        if (!queue.empty() && (!best || price > *best)) {
            best = price;
        }
    }
    best_bid_ = best;
}

void OrderBook::refresh_best_ask() {
    std::optional<std::int64_t> best;
    for (auto& [price, queue] : asks_) {
        sweep_inactive(queue);
        if (!queue.empty() && (!best || price < *best)) {
            best = price;
        }
    }
    best_ask_ = best;
}

std::optional<std::int64_t> OrderBook::best_price_for(Side side) const {
    return side == Side::Buy ? best_bid_ : best_ask_;
}

bool OrderBook::crosses(const Order& incoming) const {
    if (incoming.type == OrderType::Market) {
        return true;
    }
    if (incoming.side == Side::Buy) {
        return best_ask_ && incoming.price >= *best_ask_;
    }
    return best_bid_ && incoming.price <= *best_bid_;
}

std::unordered_map<std::int64_t, OrderBook::LevelQueue>& OrderBook::book_for(Side side) {
    return side == Side::Buy ? bids_ : asks_;
}

const std::unordered_map<std::int64_t, OrderBook::LevelQueue>& OrderBook::book_for(Side side) const {
    return side == Side::Buy ? bids_ : asks_;
}

bool OrderBook::add(Order order, const ExecutionCallback& on_execution) {
    if (order.quantity <= 0) {
        return false;
    }

    auto consume = [&](auto& contra_book, auto best_price_getter, auto refresh) {
        while (order.quantity > 0) {
            auto best = best_price_getter();
            if (!best) {
                break;
            }
            const bool price_ok = order.type == OrderType::Market ||
                (order.side == Side::Buy ? order.price >= *best : order.price <= *best);
            if (!price_ok) {
                break;
            }

            auto& queue = contra_book[*best];
            sweep_inactive(queue);
            if (queue.empty()) {
                refresh();
                continue;
            }

            auto resting = queue.front();
            const auto traded = std::min(order.quantity, resting->order.quantity);
            resting->order.quantity -= traded;
            order.quantity -= traded;
            on_execution(Execution{resting->order.id, order.id, resting->order.price, traded});

            if (resting->order.quantity == 0) {
                resting->active = false;
                order_index_.erase(resting->order.id);
                sweep_inactive(queue);
            }
            refresh();
        }
    };

    if (order.side == Side::Buy) {
        consume(asks_, [this] { return best_ask_; }, [this] { refresh_best_ask(); });
    } else {
        consume(bids_, [this] { return best_bid_; }, [this] { refresh_best_bid(); });
    }

    if (order.quantity <= 0 || order.type == OrderType::Market) {
        return true;
    }

    auto node = std::make_shared<Node>();
    node->order = order;
    auto& own_book = book_for(order.side);
    own_book[order.price].push_back(node);
    order_index_[order.id] = node;

    if (order.side == Side::Buy) {
        if (!best_bid_ || order.price > *best_bid_) {
            best_bid_ = order.price;
        }
    } else {
        if (!best_ask_ || order.price < *best_ask_) {
            best_ask_ = order.price;
        }
    }
    return true;
}

bool OrderBook::cancel(std::uint64_t order_id) {
    auto it = order_index_.find(order_id);
    if (it == order_index_.end()) {
        return false;
    }
    it->second->active = false;
    it->second->order.quantity = 0;
    const auto side = it->second->order.side;
    order_index_.erase(it);
    if (side == Side::Buy) {
        refresh_best_bid();
    } else {
        refresh_best_ask();
    }
    return true;
}

std::optional<BookSnapshot> OrderBook::snapshot() const {
    BookSnapshot snap{};
    if (best_bid_) {
        auto it = bids_.find(*best_bid_);
        if (it != bids_.end()) {
            snap.best_bid = *best_bid_;
            snap.best_bid_qty = level_quantity(it->second);
        }
    }
    if (best_ask_) {
        auto it = asks_.find(*best_ask_);
        if (it != asks_.end()) {
            snap.best_ask = *best_ask_;
            snap.best_ask_qty = level_quantity(it->second);
        }
    }
    return snap;
}

std::size_t OrderBook::size() const noexcept {
    return order_index_.size();
}

}  // namespace llmde::core
