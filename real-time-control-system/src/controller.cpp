#include "realtime/controller.hpp"

#include <algorithm>

namespace realtime {

PIDController::PIDController(const ControllerConfig& config) : config_(config) {}

double PIDController::update(double setpoint, double measurement, double dt_seconds) {
    const double error = setpoint - measurement;
    integral_ += error * dt_seconds;
    integral_ = std::clamp(integral_, config_.integral_min, config_.integral_max);

    double derivative = 0.0;
    if (has_last_error_ && dt_seconds > 0.0) {
        derivative = (error - last_error_) / dt_seconds;
    }

    const double raw_output =
        config_.kp * error +
        config_.ki * integral_ +
        config_.kd * derivative;

    const double output = std::clamp(raw_output, config_.output_min, config_.output_max);

    last_error_ = error;
    has_last_error_ = true;
    return output;
}

void PIDController::reset() {
    integral_ = 0.0;
    last_error_ = 0.0;
    has_last_error_ = false;
}

} // namespace realtime
