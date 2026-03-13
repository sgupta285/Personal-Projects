#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace daq {

struct MetricsSnapshot {
    double seconds_since_start{};
    std::uint64_t produced_total{};
    std::uint64_t accepted_total{};
    std::uint64_t source_dropped_total{};
    std::uint64_t writer_dropped_total{};
    std::uint64_t invalid_total{};
    std::uint64_t writer_batches_total{};
    std::uint64_t writer_records_total{};
    std::size_t source_queue_depth_total{};
    std::size_t writer_queue_depth{};
    double interval_throughput_msgs{};
    double interval_drop_rate{};
    double latency_avg_ms{};
    double latency_p50_ms{};
    double latency_p95_ms{};
    double latency_max_ms{};
};

struct RunSummary {
    std::string scenario;
    std::uint64_t produced_total{};
    std::uint64_t accepted_total{};
    std::uint64_t source_dropped_total{};
    std::uint64_t writer_dropped_total{};
    std::uint64_t invalid_total{};
    std::uint64_t writer_batches_total{};
    std::uint64_t writer_records_total{};
    double drop_rate{};
    double latency_avg_ms{};
    double latency_p50_ms{};
    double latency_p95_ms{};
    double latency_max_ms{};
    double duration_s{};
};

void write_metrics_csv(const std::string& path, const std::vector<MetricsSnapshot>& snapshots);
void write_summary_json(const std::string& path, const RunSummary& summary);
void write_prometheus_text(const std::string& path, const RunSummary& summary);

double percentile(std::vector<double> values, double fraction);

}  // namespace daq
