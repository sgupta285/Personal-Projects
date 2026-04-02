#pragma once

#include <cstddef>
#include <memory>
#include <vector>

namespace llmde::core {

template <typename T>
class ObjectPool {
  public:
    explicit ObjectPool(std::size_t reserve = 1024) {
        storage_.reserve(reserve);
        free_.reserve(reserve);
        for (std::size_t i = 0; i < reserve; ++i) {
            storage_.push_back(std::make_unique<T>());
            free_.push_back(storage_.back().get());
        }
    }

    T* acquire() {
        if (free_.empty()) {
            storage_.push_back(std::make_unique<T>());
            return storage_.back().get();
        }
        T* ptr = free_.back();
        free_.pop_back();
        return ptr;
    }

    void release(T* ptr) {
        free_.push_back(ptr);
    }

  private:
    std::vector<std::unique_ptr<T>> storage_;
    std::vector<T*> free_;
};

}  // namespace llmde::core
