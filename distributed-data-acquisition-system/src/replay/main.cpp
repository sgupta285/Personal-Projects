#include "core/message.hpp"
#include "core/metrics.hpp"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace daq {

struct Args {
    std::string input;
    std::size_t max_messages{0};
};

Args parse_args(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        const std::string token = argv[i];
        if (token == "--input" && i + 1 < argc) {
            args.input = argv[++i];
        } else if (token == "--max-messages" && i + 1 < argc) {
            args.max_messages = static_cast<std::size_t>(std::stoull(argv[++i]));
        } else {
            throw std::runtime_error("unknown argument: " + token);
        }
    }
    if (args.input.empty()) {
        throw std::runtime_error("missing --input path");
    }
    return args;
}

}  // namespace daq

int main(int argc, char** argv) {
    try {
        const auto args = daq::parse_args(argc, argv);
        std::ifstream in(args.input, std::ios::binary);
        if (!in) {
            throw std::runtime_error("failed to open input stream: " + args.input);
        }

        std::vector<double> latencies_ms;
        std::size_t count = 0;
        daq::BinaryRecord record{};

        while (in.read(reinterpret_cast<char*>(&record), sizeof(record))) {
            const double latency_ms = static_cast<double>(record.ingest_time_ns - record.event_time_ns) / 1'000'000.0;
            latencies_ms.push_back(latency_ms);
            ++count;

            if (args.max_messages > 0 && count <= args.max_messages) {
                std::cout << "message " << count
                          << " source=" << record.source_id
                          << " sequence=" << record.sequence
                          << " kind=" << static_cast<int>(record.kind)
                          << " value=" << std::fixed << std::setprecision(4) << record.value
                          << " latency_ms=" << latency_ms
                          << '\n';
            }
        }

        const auto parent = std::filesystem::path(args.input).parent_path();
        const auto stem = std::filesystem::path(args.input).stem().string();
        const auto summary_path = parent / (stem + "_replay_summary.json");

        daq::RunSummary summary;
        summary.scenario = stem;
        summary.accepted_total = static_cast<std::uint64_t>(count);
        summary.writer_records_total = static_cast<std::uint64_t>(count);
        summary.latency_avg_ms = latencies_ms.empty() ? 0.0 :
            std::accumulate(latencies_ms.begin(), latencies_ms.end(), 0.0) / latencies_ms.size();
        summary.latency_p50_ms = daq::percentile(latencies_ms, 0.50);
        summary.latency_p95_ms = daq::percentile(latencies_ms, 0.95);
        summary.latency_max_ms = latencies_ms.empty() ? 0.0 : *std::max_element(latencies_ms.begin(), latencies_ms.end());

        daq::write_summary_json(summary_path.string(), summary);
        std::cout << "replayed_records=" << count
                  << " replay_p95_ms=" << summary.latency_p95_ms
                  << std::endl;
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "daq_replay failed: " << ex.what() << std::endl;
        return 1;
    }
}
