#pragma once

#include <string>
#include <vector>

namespace daq {

struct ScenarioConfig {
    std::string name;
    int sources{4};
    int rate_hz{6000};
    int duration_s{3};
    int burst_every_ms{0};
    int burst_multiplier{1};
    int writer_sleep_ms{0};
    int source_queue_capacity{4096};
    int writer_queue_capacity{8192};
    int batch_size{256};
};

std::vector<ScenarioConfig> load_scenarios_from_csv(const std::string& path);
ScenarioConfig scenario_by_name(const std::vector<ScenarioConfig>& scenarios, const std::string& name);

}  // namespace daq
