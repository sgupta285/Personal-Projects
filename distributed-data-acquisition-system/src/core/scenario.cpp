#include "core/scenario.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>

namespace daq {

std::vector<ScenarioConfig> load_scenarios_from_csv(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("failed to open scenario config: " + path);
    }

    std::vector<ScenarioConfig> scenarios;
    std::string line;
    std::getline(in, line);

    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        std::stringstream ss(line);
        std::string token;
        ScenarioConfig cfg;

        std::getline(ss, cfg.name, ',');
        std::getline(ss, token, ','); cfg.sources = std::stoi(token);
        std::getline(ss, token, ','); cfg.rate_hz = std::stoi(token);
        std::getline(ss, token, ','); cfg.duration_s = std::stoi(token);
        std::getline(ss, token, ','); cfg.burst_every_ms = std::stoi(token);
        std::getline(ss, token, ','); cfg.burst_multiplier = std::stoi(token);
        std::getline(ss, token, ','); cfg.writer_sleep_ms = std::stoi(token);
        std::getline(ss, token, ','); cfg.source_queue_capacity = std::stoi(token);
        std::getline(ss, token, ','); cfg.writer_queue_capacity = std::stoi(token);
        std::getline(ss, token, ','); cfg.batch_size = std::stoi(token);

        scenarios.push_back(cfg);
    }

    return scenarios;
}

ScenarioConfig scenario_by_name(const std::vector<ScenarioConfig>& scenarios, const std::string& name) {
    for (const auto& scenario : scenarios) {
        if (scenario.name == name) {
            return scenario;
        }
    }
    throw std::runtime_error("scenario not found: " + name);
}

}  // namespace daq
