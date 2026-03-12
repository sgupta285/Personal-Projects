#pragma once

#include <deque>

#include "realtime/config.hpp"

namespace realtime {

class MovingAverageFilter {
public:
    explicit MovingAverageFilter(int window_size);
    double update(double measurement);
    void reset();

private:
    std::deque<double> window_;
    int window_size_;
    double sum_ {0.0};
};

class KalmanFilter1D {
public:
    KalmanFilter1D(double process_variance, double measurement_variance);
    double update(double measurement);
    void reset(double initial_estimate = 0.0);

private:
    double q_;
    double r_;
    double x_ {0.0};
    double p_ {1.0};
    bool initialized_ {false};
};

class FilterPipeline {
public:
    explicit FilterPipeline(const FilterConfig& config);
    double update(double measurement);
    void reset();

private:
    FilterConfig config_;
    MovingAverageFilter moving_average_;
    KalmanFilter1D kalman_;
};

} // namespace realtime
