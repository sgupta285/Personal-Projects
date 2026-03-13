#pragma once

#include <atomic>
#include <cstddef>
#include <memory>
#include <optional>

namespace daq {

template <typename T>
class SpscQueue {
public:
    explicit SpscQueue(std::size_t capacity)
        : capacity_(capacity + 1),
          buffer_(std::make_unique<T[]>(capacity_)) {}

    bool push(const T& item) {
        const auto head = head_.load(std::memory_order_relaxed);
        const auto next = increment(head);
        if (next == tail_.load(std::memory_order_acquire)) {
            return false;
        }
        buffer_[head] = item;
        head_.store(next, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() {
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T item = buffer_[tail];
        tail_.store(increment(tail), std::memory_order_release);
        return item;
    }

    [[nodiscard]] std::size_t size() const {
        const auto head = head_.load(std::memory_order_acquire);
        const auto tail = tail_.load(std::memory_order_acquire);
        if (head >= tail) {
            return head - tail;
        }
        return capacity_ - (tail - head);
    }

    [[nodiscard]] std::size_t capacity() const {
        return capacity_ - 1;
    }

private:
    [[nodiscard]] std::size_t increment(std::size_t index) const {
        return (index + 1) % capacity_;
    }

    const std::size_t capacity_;
    std::unique_ptr<T[]> buffer_;
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};

}  // namespace daq
