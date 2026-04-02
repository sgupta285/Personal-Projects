#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "llmde/core/order_book.hpp"
#include "llmde/io/udp_publisher.hpp"

namespace llmde::engine {

class MatchingEngine {
  public:
    explicit MatchingEngine(std::string symbol, std::string market_data_host = "127.0.0.1", std::uint16_t market_data_port = 19001);

    bool submit(core::Order order);
    bool cancel(std::uint64_t order_id);
    core::BookSnapshot snapshot() const;
    const std::vector<core::Execution>& recent_executions() const noexcept;

  private:
    std::string symbol_;
    core::OrderBook book_;
    io::UdpPublisher publisher_;
    std::vector<core::Execution> recent_executions_;

    void publish_execution(const core::Execution& execution);
    void publish_snapshot();
};

}  // namespace llmde::engine
