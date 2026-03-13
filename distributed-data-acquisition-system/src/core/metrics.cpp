#include "core/metrics.hpp"

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <stdexcept>

namespace daq {

double percentile(std::vector<double> values, double fraction) {
    if (values.empty()) {
        return 0.0;
    }
    std::sort(values.begin(), values.end());
    const auto idx = static_cast<std::size_t>(fraction * static_cast<double>(values.size() - 1));
    return values[idx];
}

void write_metrics_csv(const std::string& path, const std::vector<MetricsSnapshot>& snapshots) {
    std::ofstream out(path);
    if (!out) {
        throw std::runtime_error("failed to write metrics csv: " + path);
    }

    out << "seconds_since_start,produced_total,accepted_total,source_dropped_total,writer_dropped_total,"
           "invalid_total,writer_batches_total,writer_records_total,source_queue_depth_total,writer_queue_depth,"
           "interval_throughput_msgs,interval_drop_rate,latency_avg_ms,latency_p50_ms,latency_p95_ms,latency_max_ms\n";
    out << std::fixed << std::setprecision(4);
    for (const auto& row : snapshots) {
        out << row.seconds_since_start << ','
            << row.produced_total << ','
            << row.accepted_total << ','
            << row.source_dropped_total << ','
            << row.writer_dropped_total << ','
            << row.invalid_total << ','
            << row.writer_batches_total << ','
            << row.writer_records_total << ','
            << row.source_queue_depth_total << ','
            << row.writer_queue_depth << ','
            << row.interval_throughput_msgs << ','
            << row.interval_drop_rate << ','
            << row.latency_avg_ms << ','
            << row.latency_p50_ms << ','
            << row.latency_p95_ms << ','
            << row.latency_max_ms << '\n';
    }
}

void write_summary_json(const std::string& path, const RunSummary& summary) {
    std::ofstream out(path);
    if (!out) {
        throw std::runtime_error("failed to write summary json: " + path);
    }

    out << std::fixed << std::setprecision(4);
    out << "{\n";
    out << "  \"scenario\": \"" << summary.scenario << "\",\n";
    out << "  \"produced_total\": " << summary.produced_total << ",\n";
    out << "  \"accepted_total\": " << summary.accepted_total << ",\n";
    out << "  \"source_dropped_total\": " << summary.source_dropped_total << ",\n";
    out << "  \"writer_dropped_total\": " << summary.writer_dropped_total << ",\n";
    out << "  \"invalid_total\": " << summary.invalid_total << ",\n";
    out << "  \"writer_batches_total\": " << summary.writer_batches_total << ",\n";
    out << "  \"writer_records_total\": " << summary.writer_records_total << ",\n";
    out << "  \"drop_rate\": " << summary.drop_rate << ",\n";
    out << "  \"latency_avg_ms\": " << summary.latency_avg_ms << ",\n";
    out << "  \"latency_p50_ms\": " << summary.latency_p50_ms << ",\n";
    out << "  \"latency_p95_ms\": " << summary.latency_p95_ms << ",\n";
    out << "  \"latency_max_ms\": " << summary.latency_max_ms << ",\n";
    out << "  \"duration_s\": " << summary.duration_s << "\n";
    out << "}\n";
}

void write_prometheus_text(const std::string& path, const RunSummary& summary) {
    std::ofstream out(path);
    if (!out) {
        throw std::runtime_error("failed to write metrics export: " + path);
    }

    out << "# TYPE daq_produced_total counter\n";
    out << "daq_produced_total " << summary.produced_total << "\n";
    out << "# TYPE daq_accepted_total counter\n";
    out << "daq_accepted_total " << summary.accepted_total << "\n";
    out << "# TYPE daq_drop_rate gauge\n";
    out << "daq_drop_rate " << summary.drop_rate << "\n";
    out << "# TYPE daq_latency_p95_ms gauge\n";
    out << "daq_latency_p95_ms " << summary.latency_p95_ms << "\n";
}

}  // namespace daq
