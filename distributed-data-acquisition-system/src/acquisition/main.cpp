#include "core/message.hpp"
#include "core/metrics.hpp"
#include "core/scenario.hpp"
#include "core/spsc_queue.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

using Clock = std::chrono::steady_clock;

namespace daq {

struct SharedCounters {
    std::atomic<std::uint64_t> produced_total{0};
    std::atomic<std::uint64_t> accepted_total{0};
    std::atomic<std::uint64_t> source_dropped_total{0};
    std::atomic<std::uint64_t> writer_dropped_total{0};
    std::atomic<std::uint64_t> invalid_total{0};
    std::atomic<std::uint64_t> writer_batches_total{0};
    std::atomic<std::uint64_t> writer_records_total{0};
};

struct ProducerStats {
    std::uint64_t produced{0};
    std::uint64_t dropped{0};
};

struct Args {
    std::string scenario{"baseline"};
    std::string config_path{"config/scenarios.csv"};
    std::string output_dir{"data/generated"};
};

std::uint64_t now_ns() {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count());
}

Args parse_args(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        const std::string token = argv[i];
        if (token == "--scenario" && i + 1 < argc) {
            args.scenario = argv[++i];
        } else if (token == "--config" && i + 1 < argc) {
            args.config_path = argv[++i];
        } else if (token == "--output-dir" && i + 1 < argc) {
            args.output_dir = argv[++i];
        } else {
            throw std::runtime_error("unknown argument: " + token);
        }
    }
    return args;
}

void producer_loop(
    int source_idx,
    const ScenarioConfig& scenario,
    SpscQueue<Message>& queue,
    SharedCounters& counters,
    std::atomic<bool>& stop_flag,
    ProducerStats& stats) {

    using namespace std::chrono;
    const auto base_interval = nanoseconds(static_cast<long long>(1'000'000'000.0 / static_cast<double>(scenario.rate_hz)));
    auto next_send = Clock::now();
    const auto run_start = Clock::now();
    std::uint64_t sequence = 0;

    while (!stop_flag.load(std::memory_order_relaxed)) {
        const auto current = Clock::now();
        if (current < next_send) {
            std::this_thread::sleep_until(next_send);
        }

        const auto elapsed_ms = duration_cast<milliseconds>(Clock::now() - run_start).count();
        int effective_multiplier = 1;
        if (scenario.burst_every_ms > 0) {
            const auto cycle = elapsed_ms / scenario.burst_every_ms;
            if (cycle % 2 == 1) {
                effective_multiplier = scenario.burst_multiplier;
            }
        }

        for (int i = 0; i < effective_multiplier && !stop_flag.load(std::memory_order_relaxed); ++i) {
            Message message;
            message.source_id = static_cast<std::uint64_t>(source_idx);
            message.sequence = ++sequence;
            message.event_time_ns = now_ns();
            message.ingest_time_ns = 0;
            message.value = std::sin(static_cast<double>(sequence) * 0.01 + static_cast<double>(source_idx));
            message.kind = (sequence % 20 == 0) ? MessageKind::Heartbeat : MessageKind::Measurement;
            message.valid = (sequence % 997 == 0) ? 0 : 1;

            if (queue.push(message)) {
                ++stats.produced;
                counters.produced_total.fetch_add(1, std::memory_order_relaxed);
            } else {
                ++stats.dropped;
                counters.source_dropped_total.fetch_add(1, std::memory_order_relaxed);
            }
        }

        next_send += base_interval;
    }
}

void writer_loop(
    const ScenarioConfig& scenario,
    SpscQueue<Message>& writer_queue,
    SharedCounters& counters,
    const std::filesystem::path& stream_path,
    std::atomic<bool>& ingest_finished) {

    std::ofstream out(stream_path, std::ios::binary);
    if (!out) {
        throw std::runtime_error("failed to open output stream: " + stream_path.string());
    }

    std::vector<BinaryRecord> batch;
    batch.reserve(static_cast<std::size_t>(scenario.batch_size));

    while (!ingest_finished.load(std::memory_order_relaxed) || writer_queue.size() > 0) {
        auto record = writer_queue.pop();
        if (!record.has_value()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        } else {
            batch.push_back(to_record(*record));
        }

        if (batch.size() >= static_cast<std::size_t>(scenario.batch_size) ||
            (!batch.empty() && (ingest_finished.load(std::memory_order_relaxed) && writer_queue.size() == 0))) {
            out.write(reinterpret_cast<const char*>(batch.data()), static_cast<std::streamsize>(batch.size() * sizeof(BinaryRecord)));
            counters.writer_records_total.fetch_add(batch.size(), std::memory_order_relaxed);
            counters.writer_batches_total.fetch_add(1, std::memory_order_relaxed);
            batch.clear();
            if (scenario.writer_sleep_ms > 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(scenario.writer_sleep_ms));
            }
        }
    }
}

int run(const ScenarioConfig& scenario, const std::string& output_dir) {
    std::filesystem::create_directories(output_dir);

    std::vector<std::unique_ptr<SpscQueue<Message>>> source_queues;
    source_queues.reserve(static_cast<std::size_t>(scenario.sources));
    for (int i = 0; i < scenario.sources; ++i) {
        source_queues.emplace_back(std::make_unique<SpscQueue<Message>>(static_cast<std::size_t>(scenario.source_queue_capacity)));
    }

    SpscQueue<Message> writer_queue(static_cast<std::size_t>(scenario.writer_queue_capacity));
    SharedCounters counters;
    std::atomic<bool> stop_flag{false};
    std::atomic<bool> ingest_finished{false};

    std::vector<ProducerStats> producer_stats(static_cast<std::size_t>(scenario.sources));
    std::vector<std::thread> producers;
    producers.reserve(static_cast<std::size_t>(scenario.sources));

    for (int i = 0; i < scenario.sources; ++i) {
        producers.emplace_back(producer_loop,
            i + 1,
            std::cref(scenario),
            std::ref(*source_queues[static_cast<std::size_t>(i)]),
            std::ref(counters),
            std::ref(stop_flag),
            std::ref(producer_stats[static_cast<std::size_t>(i)]));
    }

    const auto stream_path = std::filesystem::path(output_dir) / (scenario.name + "_stream.bin");
    std::thread writer(writer_loop, std::cref(scenario), std::ref(writer_queue), std::ref(counters), stream_path, std::ref(ingest_finished));

    std::vector<MetricsSnapshot> snapshots;
    std::vector<double> all_latencies_ms;
    const auto start = Clock::now();
    auto next_metrics_tick = start + std::chrono::milliseconds(200);
    std::uint64_t last_accepted = 0;
    std::uint64_t last_dropped = 0;

    while (Clock::now() - start < std::chrono::seconds(scenario.duration_s)) {
        std::size_t queue_depth_total = 0;
        std::vector<double> interval_latencies_ms;

        for (auto& queue : source_queues) {
            queue_depth_total += queue->size();
            while (auto message = queue->pop()) {
                if (!message->valid) {
                    counters.invalid_total.fetch_add(1, std::memory_order_relaxed);
                    continue;
                }

                message->ingest_time_ns = now_ns();
                const auto latency_ms = static_cast<double>(message->ingest_time_ns - message->event_time_ns) / 1'000'000.0;

                if (writer_queue.size() > writer_queue.capacity() * 7 / 10 &&
                    message->kind == MessageKind::Heartbeat) {
                    counters.writer_dropped_total.fetch_add(1, std::memory_order_relaxed);
                    continue;
                }

                if (!writer_queue.push(*message)) {
                    counters.writer_dropped_total.fetch_add(1, std::memory_order_relaxed);
                    continue;
                }

                counters.accepted_total.fetch_add(1, std::memory_order_relaxed);
                interval_latencies_ms.push_back(latency_ms);
                all_latencies_ms.push_back(latency_ms);
            }
        }

        const auto now = Clock::now();
        if (now >= next_metrics_tick) {
            const auto accepted_total = counters.accepted_total.load(std::memory_order_relaxed);
            const auto dropped_total =
                counters.source_dropped_total.load(std::memory_order_relaxed) +
                counters.writer_dropped_total.load(std::memory_order_relaxed);
            const auto interval_accepted = accepted_total - last_accepted;
            const auto interval_dropped = dropped_total - last_dropped;
            const auto interval_total = static_cast<double>(interval_accepted + interval_dropped);
            const auto interval_drop_rate = interval_total > 0.0 ? static_cast<double>(interval_dropped) / interval_total : 0.0;

            MetricsSnapshot snapshot;
            snapshot.seconds_since_start = std::chrono::duration<double>(now - start).count();
            snapshot.produced_total = counters.produced_total.load(std::memory_order_relaxed);
            snapshot.accepted_total = accepted_total;
            snapshot.source_dropped_total = counters.source_dropped_total.load(std::memory_order_relaxed);
            snapshot.writer_dropped_total = counters.writer_dropped_total.load(std::memory_order_relaxed);
            snapshot.invalid_total = counters.invalid_total.load(std::memory_order_relaxed);
            snapshot.writer_batches_total = counters.writer_batches_total.load(std::memory_order_relaxed);
            snapshot.writer_records_total = counters.writer_records_total.load(std::memory_order_relaxed);
            snapshot.source_queue_depth_total = queue_depth_total;
            snapshot.writer_queue_depth = writer_queue.size();
            snapshot.interval_throughput_msgs = interval_accepted / 0.2;
            snapshot.interval_drop_rate = interval_drop_rate;
            snapshot.latency_avg_ms = interval_latencies_ms.empty() ? 0.0 :
                std::accumulate(interval_latencies_ms.begin(), interval_latencies_ms.end(), 0.0) / interval_latencies_ms.size();
            snapshot.latency_p50_ms = percentile(interval_latencies_ms, 0.50);
            snapshot.latency_p95_ms = percentile(interval_latencies_ms, 0.95);
            snapshot.latency_max_ms = interval_latencies_ms.empty() ? 0.0 :
                *std::max_element(interval_latencies_ms.begin(), interval_latencies_ms.end());

            snapshots.push_back(snapshot);
            last_accepted = accepted_total;
            last_dropped = dropped_total;
            next_metrics_tick += std::chrono::milliseconds(200);
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    stop_flag.store(true, std::memory_order_relaxed);
    for (auto& thread : producers) {
        thread.join();
    }

    while (true) {
        bool drained = true;
        for (auto& queue : source_queues) {
            if (queue->size() > 0) {
                drained = false;
                while (auto message = queue->pop()) {
                    if (!message->valid) {
                        counters.invalid_total.fetch_add(1, std::memory_order_relaxed);
                        continue;
                    }
                    message->ingest_time_ns = now_ns();
                    const auto latency_ms = static_cast<double>(message->ingest_time_ns - message->event_time_ns) / 1'000'000.0;
                    all_latencies_ms.push_back(latency_ms);
                    if (!writer_queue.push(*message)) {
                        counters.writer_dropped_total.fetch_add(1, std::memory_order_relaxed);
                    } else {
                        counters.accepted_total.fetch_add(1, std::memory_order_relaxed);
                    }
                }
            }
        }
        if (drained) {
            break;
        }
    }

    ingest_finished.store(true, std::memory_order_relaxed);
    writer.join();

    RunSummary summary;
    summary.scenario = scenario.name;
    summary.produced_total = counters.produced_total.load(std::memory_order_relaxed);
    summary.accepted_total = counters.accepted_total.load(std::memory_order_relaxed);
    summary.source_dropped_total = counters.source_dropped_total.load(std::memory_order_relaxed);
    summary.writer_dropped_total = counters.writer_dropped_total.load(std::memory_order_relaxed);
    summary.invalid_total = counters.invalid_total.load(std::memory_order_relaxed);
    summary.writer_batches_total = counters.writer_batches_total.load(std::memory_order_relaxed);
    summary.writer_records_total = counters.writer_records_total.load(std::memory_order_relaxed);
    const auto drop_total = summary.source_dropped_total + summary.writer_dropped_total;
    const auto attempted_total = summary.accepted_total + drop_total;
    summary.drop_rate = attempted_total > 0 ? static_cast<double>(drop_total) / static_cast<double>(attempted_total) : 0.0;
    summary.latency_avg_ms = all_latencies_ms.empty() ? 0.0 :
        std::accumulate(all_latencies_ms.begin(), all_latencies_ms.end(), 0.0) / all_latencies_ms.size();
    summary.latency_p50_ms = percentile(all_latencies_ms, 0.50);
    summary.latency_p95_ms = percentile(all_latencies_ms, 0.95);
    summary.latency_max_ms = all_latencies_ms.empty() ? 0.0 :
        *std::max_element(all_latencies_ms.begin(), all_latencies_ms.end());
    summary.duration_s = std::chrono::duration<double>(Clock::now() - start).count();

    const auto metrics_path = std::filesystem::path(output_dir) / (scenario.name + "_metrics.csv");
    const auto summary_path = std::filesystem::path(output_dir) / (scenario.name + "_summary.json");
    const auto prom_path = std::filesystem::path(output_dir) / (scenario.name + "_metrics.prom");

    write_metrics_csv(metrics_path.string(), snapshots);
    write_summary_json(summary_path.string(), summary);
    write_prometheus_text(prom_path.string(), summary);

    std::cout << "scenario=" << scenario.name
              << " accepted=" << summary.accepted_total
              << " drops=" << drop_total
              << " p95_latency_ms=" << summary.latency_p95_ms
              << std::endl;
    return 0;
}

}  // namespace daq

int main(int argc, char** argv) {
    try {
        const auto args = daq::parse_args(argc, argv);
        const auto scenarios = daq::load_scenarios_from_csv(args.config_path);
        const auto scenario = daq::scenario_by_name(scenarios, args.scenario);
        return daq::run(scenario, args.output_dir);
    } catch (const std::exception& ex) {
        std::cerr << "daq_acquire failed: " << ex.what() << std::endl;
        return 1;
    }
}
