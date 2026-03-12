#pragma once

#include "realtime/config.hpp"

namespace realtime {

class PIDController {
public:
    explicit PIDController(const ControllerConfig& config);
    double update(double setpoint, double measurement, double dt_seconds);
    void reset();

    double integral_term() const { return integral_; }
    double last_error() const { return last_error_; }

private:
    ControllerConfig config_;
    double integral_ {0.0};
    double last_error_ {0.0};
    bool has_last_error_ {false};
};

} // namespace realtime
