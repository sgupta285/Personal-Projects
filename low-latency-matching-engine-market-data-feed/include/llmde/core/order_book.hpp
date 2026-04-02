#pragma once

#include <cstdint>
#include <deque>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>

#include "llmde/core/order.hpp"

namespace llmde::core {

class OrderBook {
  public:
    using ExecutionCallback = std::function<void(const Execution&)>;

    bool add(Order order, const ExecutionCallback& on_execution);
    bool cancel(std::uint64_t order_id);
    std::optional<BookSnapshot> snapshot() const;
    std::size_t size() const noexcept;

  private:
    struct Node {
        Order order;
        bool active{true};
    };

    using LevelQueue = std::deque<std::shared_ptr<Node>>;

    std::unordered_map<std::int64_t, LevelQueue> bids_;
    std::unordered_map<std::int64_t, LevelQueue> asks_;
    std::unordered_map<std::uint64_t, std::shared_ptr<Node>> order_index_;
    std::optional<std::int64_t> best_bid_;
    std::optional<std::int64_t> best_ask_;

    static std::int64_t level_quantity(const LevelQueue& queue);
    void sweep_inactive(LevelQueue& queue);
    void refresh_best_bid();
    void refresh_best_ask();
    bool crosses(const Order& incoming) const;
    std::optional<std::int64_t> best_price_for(Side side) const;
    std::unordered_map<std::int64_t, LevelQueue>& book_for(Side side);
    const std::unordered_map<std::int64_t, LevelQueue>& book_for(Side side) const;
};

}  // namespace llmde::core
