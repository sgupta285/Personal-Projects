#pragma once

#include <string>
#include <vector>

namespace realtime {

struct ControllerConfig {
    double kp {0.12};
    double ki {0.35};
    double kd {0.01};
    double integral_min {-80.0};
    double integral_max {80.0};
    double output_min {0.0};
    double output_max {100.0};
};

struct FilterConfig {
    std::string type {"kalman"};
    int moving_average_window {5};
    double kalman_process_variance {0.08};
    double kalman_measurement_variance {6.0};
};

struct SetpointStep {
    double time_s {0.0};
    double value {0.0};
};

struct SimulationConfig {
    double duration_seconds {12.0};
    int control_period_ms {10};
    int sensor_period_ms {10};
    int max_sensor_delay_ms {30};
    double noise_stddev {2.0};
    double plant_gain {1.0};
    double plant_time_constant {0.35};
    double disturbance_start_s {6.0};
    double disturbance_end_s {7.0};
    double disturbance_magnitude {-35.0};
    ControllerConfig controller {};
    FilterConfig filter {};
    std::vector<SetpointStep> setpoint_profile {};
};

SimulationConfig load_config(const std::string& path);
double setpoint_for_time(const SimulationConfig& config, double time_s);

} // namespace realtime
