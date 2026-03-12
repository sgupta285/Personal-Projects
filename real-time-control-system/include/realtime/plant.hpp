#pragma once

namespace realtime {

class MotorPlant {
public:
    MotorPlant(double gain, double time_constant);
    void reset(double initial_speed = 0.0);
    double update(double control_input, double disturbance, double dt_seconds);
    double speed() const { return speed_; }

private:
    double gain_;
    double time_constant_;
    double speed_ {0.0};
};

} // namespace realtime
