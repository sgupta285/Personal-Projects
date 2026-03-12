#include <cmath>
#include <iostream>
#include <string>

#include "realtime/config.hpp"
#include "realtime/controller.hpp"
#include "realtime/filter.hpp"
#include "realtime/plant.hpp"

using namespace realtime;

namespace {

void assert_true(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "Test failed: " << message << '\n';
        std::exit(1);
    }
}

void test_pid_moves_toward_setpoint() {
    ControllerConfig cfg;
    cfg.kp = 2.0;
    cfg.ki = 1.5;
    cfg.kd = 0.05;
    cfg.output_max = 100.0;
    PIDController controller(cfg);
    MotorPlant plant(1.0, 0.30);

    double measurement = 0.0;
    for (int i = 0; i < 500; ++i) {
        const double output = controller.update(50.0, measurement, 0.01);
        measurement = plant.update(output, 0.0, 0.01);
    }

    assert_true(std::abs(measurement - 50.0) < 8.0, "closed loop should settle near setpoint");
}

void test_moving_average_reduces_spike() {
    MovingAverageFilter filter(4);
    filter.update(10.0);
    filter.update(10.0);
    filter.update(10.0);
    const double smoothed = filter.update(30.0);
    assert_true(smoothed < 20.0, "moving average should damp spikes");
}

void test_kalman_tracks_measurement() {
    KalmanFilter1D filter(0.1, 5.0);
    double estimate = 0.0;
    for (int i = 0; i < 50; ++i) {
        estimate = filter.update(25.0);
    }
    assert_true(std::abs(estimate - 25.0) < 1.0, "kalman filter should converge toward stable measurement");
}

void test_setpoint_lookup() {
    SimulationConfig cfg;
    cfg.setpoint_profile = {{0.0, 0.0}, {1.0, 25.0}, {2.5, 55.0}};
    assert_true(setpoint_for_time(cfg, 0.2) == 0.0, "early setpoint should match first step");
    assert_true(setpoint_for_time(cfg, 1.5) == 25.0, "mid setpoint should match second step");
    assert_true(setpoint_for_time(cfg, 3.0) == 55.0, "late setpoint should match final step");
}

} // namespace

int main() {
    test_pid_moves_toward_setpoint();
    test_moving_average_reduces_spike();
    test_kalman_tracks_measurement();
    test_setpoint_lookup();
    std::cout << "All realtime control tests passed\n";
    return 0;
}
