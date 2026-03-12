#include "realtime/plant.hpp"

namespace realtime {

MotorPlant::MotorPlant(double gain, double time_constant)
    : gain_(gain), time_constant_(time_constant > 0.0 ? time_constant : 0.1) {}

void MotorPlant::reset(double initial_speed) {
    speed_ = initial_speed;
}

double MotorPlant::update(double control_input, double disturbance, double dt_seconds) {
    const double target = gain_ * control_input + disturbance;
    const double derivative = (target - speed_) / time_constant_;
    speed_ += derivative * dt_seconds;
    if (speed_ < 0.0) {
        speed_ = 0.0;
    }
    return speed_;
}

} // namespace realtime
