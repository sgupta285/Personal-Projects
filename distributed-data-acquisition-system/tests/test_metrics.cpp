#include "core/metrics.hpp"

#include <cassert>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <vector>

int main() {
    std::vector<double> values{1.0, 2.0, 3.0, 4.0, 5.0};
    const double p50 = daq::percentile(values, 0.50);
    const double p95 = daq::percentile(values, 0.95);

    assert(std::fabs(p50 - 3.0) < 1e-9);
    assert(p95 >= 4.0);

    daq::RunSummary summary;
    summary.scenario = "unit";
    summary.produced_total = 10;
    summary.accepted_total = 9;
    summary.drop_rate = 0.1;
    summary.latency_p95_ms = 1.7;

    daq::write_summary_json("tests_summary_tmp.json", summary);
    daq::write_prometheus_text("tests_prom_tmp.prom", summary);
    assert(std::filesystem::exists("tests_summary_tmp.json"));
    assert(std::filesystem::exists("tests_prom_tmp.prom"));
    std::filesystem::remove("tests_summary_tmp.json");
    std::filesystem::remove("tests_prom_tmp.prom");

    std::cout << "metrics test passed\n";
    return 0;
}
