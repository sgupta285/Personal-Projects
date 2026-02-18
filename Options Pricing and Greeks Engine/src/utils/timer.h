#pragma once
#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>

namespace opt {
class Timer {
    std::chrono::high_resolution_clock::time_point start_;
    std::string label_;
public:
    explicit Timer(const std::string& label = "") : label_(label) { start_ = std::chrono::high_resolution_clock::now(); }
    double elapsed_ms() const {
        auto now = std::chrono::high_resolution_clock::now();
        return std::chrono::duration<double, std::milli>(now - start_).count();
    }
    ~Timer() {
        if (!label_.empty()) {
            std::cout << "[" << label_ << "] " << std::fixed << std::setprecision(2) << elapsed_ms() << " ms\n";
        }
    }
};
} // namespace opt
