#include "realtime/filter.hpp"

#include <numeric>

namespace realtime {

MovingAverageFilter::MovingAverageFilter(int window_size)
    : window_size_(window_size > 0 ? window_size : 1) {}

double MovingAverageFilter::update(double measurement) {
    window_.push_back(measurement);
    sum_ += measurement;
    while (static_cast<int>(window_.size()) > window_size_) {
        sum_ -= window_.front();
        window_.pop_front();
    }
    return sum_ / static_cast<double>(window_.size());
}

void MovingAverageFilter::reset() {
    window_.clear();
    sum_ = 0.0;
}

KalmanFilter1D::KalmanFilter1D(double process_variance, double measurement_variance)
    : q_(process_variance), r_(measurement_variance) {}

double KalmanFilter1D::update(double measurement) {
    if (!initialized_) {
        x_ = measurement;
        p_ = 1.0;
        initialized_ = true;
        return x_;
    }

    p_ += q_;
    const double k = p_ / (p_ + r_);
    x_ = x_ + k * (measurement - x_);
    p_ = (1.0 - k) * p_;
    return x_;
}

void KalmanFilter1D::reset(double initial_estimate) {
    x_ = initial_estimate;
    p_ = 1.0;
    initialized_ = false;
}

FilterPipeline::FilterPipeline(const FilterConfig& config)
    : config_(config),
      moving_average_(config.moving_average_window),
      kalman_(config.kalman_process_variance, config.kalman_measurement_variance) {}

double FilterPipeline::update(double measurement) {
    if (config_.type == "moving_average") {
        return moving_average_.update(measurement);
    }
    if (config_.type == "kalman") {
        return kalman_.update(measurement);
    }
    return measurement;
}

void FilterPipeline::reset() {
    moving_average_.reset();
    kalman_.reset();
}

} // namespace realtime
