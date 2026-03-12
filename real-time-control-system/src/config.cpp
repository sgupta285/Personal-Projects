#include "realtime/config.hpp"

#include <fstream>
#include <regex>
#include <sstream>
#include <stdexcept>

namespace realtime {
namespace {

std::string read_all(const std::string& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("Could not open config file: " + path);
    }
    std::ostringstream buffer;
    buffer << input.rdbuf();
    return buffer.str();
}

double extract_number(const std::string& text, const std::string& key, double fallback) {
    const std::regex pattern("\\\"" + key + "\\\"\\s*:\\s*(-?[0-9]+(?:\\.[0-9]+)?)");
    std::smatch match;
    if (std::regex_search(text, match, pattern)) {
        return std::stod(match[1].str());
    }
    return fallback;
}

std::string extract_string(const std::string& text, const std::string& key, const std::string& fallback) {
    const std::regex pattern("\\\"" + key + "\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"");
    std::smatch match;
    if (std::regex_search(text, match, pattern)) {
        return match[1].str();
    }
    return fallback;
}

std::vector<SetpointStep> extract_setpoints(const std::string& text) {
    std::vector<SetpointStep> points;
    const std::regex pattern("\\{\\s*\\\"time_s\\\"\\s*:\\s*(-?[0-9]+(?:\\.[0-9]+)?)\\s*,\\s*\\\"value\\\"\\s*:\\s*(-?[0-9]+(?:\\.[0-9]+)?)\\s*\\}");
    auto begin = std::sregex_iterator(text.begin(), text.end(), pattern);
    auto end = std::sregex_iterator();
    for (auto it = begin; it != end; ++it) {
        points.push_back(SetpointStep{std::stod((*it)[1].str()), std::stod((*it)[2].str())});
    }
    if (points.empty()) {
        points.push_back(SetpointStep{0.0, 0.0});
        points.push_back(SetpointStep{1.0, 40.0});
    }
    return points;
}

} // namespace

SimulationConfig load_config(const std::string& path) {
    const auto text = read_all(path);
    SimulationConfig config;
    config.duration_seconds = extract_number(text, "duration_seconds", config.duration_seconds);
    config.control_period_ms = static_cast<int>(extract_number(text, "control_period_ms", config.control_period_ms));
    config.sensor_period_ms = static_cast<int>(extract_number(text, "sensor_period_ms", config.sensor_period_ms));
    config.max_sensor_delay_ms = static_cast<int>(extract_number(text, "max_sensor_delay_ms", config.max_sensor_delay_ms));
    config.noise_stddev = extract_number(text, "noise_stddev", config.noise_stddev);
    config.plant_gain = extract_number(text, "plant_gain", config.plant_gain);
    config.plant_time_constant = extract_number(text, "plant_time_constant", config.plant_time_constant);
    config.disturbance_start_s = extract_number(text, "disturbance_start_s", config.disturbance_start_s);
    config.disturbance_end_s = extract_number(text, "disturbance_end_s", config.disturbance_end_s);
    config.disturbance_magnitude = extract_number(text, "disturbance_magnitude", config.disturbance_magnitude);

    config.controller.kp = extract_number(text, "kp", config.controller.kp);
    config.controller.ki = extract_number(text, "ki", config.controller.ki);
    config.controller.kd = extract_number(text, "kd", config.controller.kd);
    config.controller.integral_min = extract_number(text, "integral_min", config.controller.integral_min);
    config.controller.integral_max = extract_number(text, "integral_max", config.controller.integral_max);
    config.controller.output_min = extract_number(text, "output_min", config.controller.output_min);
    config.controller.output_max = extract_number(text, "output_max", config.controller.output_max);

    config.filter.type = extract_string(text, "type", config.filter.type);
    config.filter.moving_average_window = static_cast<int>(extract_number(text, "moving_average_window", config.filter.moving_average_window));
    config.filter.kalman_process_variance = extract_number(text, "kalman_process_variance", config.filter.kalman_process_variance);
    config.filter.kalman_measurement_variance = extract_number(text, "kalman_measurement_variance", config.filter.kalman_measurement_variance);
    config.setpoint_profile = extract_setpoints(text);
    return config;
}

double setpoint_for_time(const SimulationConfig& config, double time_s) {
    double current = config.setpoint_profile.front().value;
    for (const auto& step : config.setpoint_profile) {
        if (time_s >= step.time_s) {
            current = step.value;
        } else {
            break;
        }
    }
    return current;
}

} // namespace realtime
