#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "realtime/config.hpp"
#include "realtime/controller.hpp"
#include "realtime/filter.hpp"
#include "realtime/plant.hpp"

namespace fs = std::filesystem;
using clock_type = std::chrono::steady_clock;

namespace realtime {

struct SensorSample {
    double timestamp_s {0.0};
    double true_speed {0.0};
    double raw_measurement {0.0};
    double filtered_measurement {0.0};
    int delay_ms {0};
};

struct SharedState {
    std::mutex mutex;
    double control_output {0.0};
    double plant_speed {0.0};
    SensorSample latest_sample {};
    bool sample_available {false};
};

struct SimulationMetrics {
    std::vector<double> jitter_ms;
    int overruns {0};
};

std::string get_arg(int argc, char** argv, const std::string& key, const std::string& fallback) {
    for (int i = 1; i < argc - 1; ++i) {
        if (argv[i] == key) {
            return argv[i + 1];
        }
    }
    return fallback;
}

void ensure_parent_directory(const std::string& path) {
    fs::path output_path(path);
    if (output_path.has_parent_path()) {
        fs::create_directories(output_path.parent_path());
    }
}

void run_sensor_thread(
    const SimulationConfig& config,
    SharedState& state,
    std::atomic<bool>& running,
    clock_type::time_point start_time
) {
    FilterPipeline filter(config.filter);
    std::mt19937 rng(42);
    std::normal_distribution<double> noise(0.0, config.noise_stddev);
    std::uniform_int_distribution<int> delay_distribution(0, std::max(config.max_sensor_delay_ms, 0));

    const auto period = std::chrono::milliseconds(config.sensor_period_ms);
    auto next_tick = clock_type::now();

    while (running.load()) {
        next_tick += period;
        std::this_thread::sleep_until(next_tick);

        const int delay_ms = delay_distribution(rng);
        if (delay_ms > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
        }

        double current_speed = 0.0;
        {
            std::lock_guard<std::mutex> lock(state.mutex);
            current_speed = state.plant_speed;
        }

        const auto now = clock_type::now();
        const double timestamp_s = std::chrono::duration<double>(now - start_time).count();
        const double raw_measurement = current_speed + noise(rng);
        const double filtered_measurement = filter.update(raw_measurement);

        SensorSample sample;
        sample.timestamp_s = timestamp_s;
        sample.true_speed = current_speed;
        sample.raw_measurement = raw_measurement;
        sample.filtered_measurement = filtered_measurement;
        sample.delay_ms = delay_ms;

        {
            std::lock_guard<std::mutex> lock(state.mutex);
            state.latest_sample = sample;
            state.sample_available = true;
        }
    }
}

int main(int argc, char** argv) {
    const std::string config_path = get_arg(argc, argv, "--config", "examples/config/default.json");
    const std::string output_path = get_arg(argc, argv, "--output", "data/logs/run.csv");

    SimulationConfig config;
    try {
        config = load_config(config_path);
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << '\n';
        return 1;
    }

    ensure_parent_directory(output_path);

    MotorPlant plant(config.plant_gain, config.plant_time_constant);
    PIDController controller(config.controller);
    SharedState state;
    SimulationMetrics metrics;
    std::atomic<bool> running {true};

    const auto start_time = clock_type::now();
    std::thread sensor_thread(run_sensor_thread, std::cref(config), std::ref(state), std::ref(running), start_time);

    std::ofstream csv(output_path);
    csv << "time_s,setpoint,true_speed,raw_measurement,filtered_measurement,control_output,error,jitter_ms,sensor_delay_ms,overrun\n";

    const auto period = std::chrono::milliseconds(config.control_period_ms);
    auto next_tick = clock_type::now();
    const int total_steps = static_cast<int>((config.duration_seconds * 1000.0) / config.control_period_ms);

    for (int step = 0; step < total_steps; ++step) {
        next_tick += period;
        std::this_thread::sleep_until(next_tick);
        const auto loop_start = clock_type::now();
        const double jitter_ms = std::chrono::duration<double, std::milli>(loop_start - next_tick).count();

        const double elapsed_s = std::chrono::duration<double>(loop_start - start_time).count();
        const double setpoint = setpoint_for_time(config, elapsed_s);

        SensorSample sample;
        {
            std::lock_guard<std::mutex> lock(state.mutex);
            sample = state.latest_sample;
            if (!state.sample_available) {
                sample.filtered_measurement = state.plant_speed;
                sample.raw_measurement = state.plant_speed;
                sample.true_speed = state.plant_speed;
            }
        }

        const double control_output = controller.update(setpoint, sample.filtered_measurement, config.control_period_ms / 1000.0);
        const double disturbance = (elapsed_s >= config.disturbance_start_s && elapsed_s <= config.disturbance_end_s)
            ? config.disturbance_magnitude
            : 0.0;
        const double true_speed = plant.update(control_output, disturbance, config.control_period_ms / 1000.0);

        {
            std::lock_guard<std::mutex> lock(state.mutex);
            state.control_output = control_output;
            state.plant_speed = true_speed;
        }

        const auto loop_end = clock_type::now();
        const double actual_loop_ms = std::chrono::duration<double, std::milli>(loop_end - loop_start).count();
        const bool overrun = actual_loop_ms > static_cast<double>(config.control_period_ms);

        metrics.jitter_ms.push_back(jitter_ms);
        if (overrun) {
            metrics.overruns += 1;
        }

        const double error = setpoint - sample.filtered_measurement;
        csv << std::fixed << std::setprecision(6)
            << elapsed_s << ','
            << setpoint << ','
            << true_speed << ','
            << sample.raw_measurement << ','
            << sample.filtered_measurement << ','
            << control_output << ','
            << error << ','
            << jitter_ms << ','
            << sample.delay_ms << ','
            << (overrun ? 1 : 0) << '\n';
    }

    running.store(false);
    sensor_thread.join();
    csv.close();

    const double max_abs_jitter = metrics.jitter_ms.empty()
        ? 0.0
        : *std::max_element(metrics.jitter_ms.begin(), metrics.jitter_ms.end(), [](double a, double b) {
            return std::abs(a) < std::abs(b);
        });

    const double average_jitter = metrics.jitter_ms.empty()
        ? 0.0
        : std::accumulate(metrics.jitter_ms.begin(), metrics.jitter_ms.end(), 0.0) / static_cast<double>(metrics.jitter_ms.size());

    fs::path summary_path = fs::path(output_path).parent_path() / "summary.json";
    std::ofstream summary(summary_path.string());
    summary << "{\n"
            << "  \"rows\": " << total_steps << ",\n"
            << "  \"overruns\": " << metrics.overruns << ",\n"
            << "  \"average_jitter_ms\": " << std::fixed << std::setprecision(6) << average_jitter << ",\n"
            << "  \"max_abs_jitter_ms\": " << std::fixed << std::setprecision(6) << std::abs(max_abs_jitter) << "\n"
            << "}\n";

    std::cout << "Simulation complete. Wrote " << output_path << '\n';
    std::cout << "Overruns: " << metrics.overruns << '\n';
    return 0;
}

} // namespace realtime

int main(int argc, char** argv) {
    return realtime::main(argc, argv);
}
