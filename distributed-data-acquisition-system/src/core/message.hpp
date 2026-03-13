#pragma once

#include <cstdint>
#include <cstddef>

namespace daq {

enum class MessageKind : std::uint8_t {
    Measurement = 1,
    Heartbeat = 2
};

struct Message {
    std::uint64_t source_id{};
    std::uint64_t sequence{};
    std::uint64_t event_time_ns{};
    std::uint64_t ingest_time_ns{};
    double value{};
    MessageKind kind{MessageKind::Measurement};
    std::uint8_t valid{1};
    std::uint16_t reserved{0};
};

struct BinaryRecord {
    std::uint64_t source_id{};
    std::uint64_t sequence{};
    std::uint64_t event_time_ns{};
    std::uint64_t ingest_time_ns{};
    double value{};
    std::uint8_t kind{};
    std::uint8_t valid{};
    std::uint16_t reserved{};
};

static_assert(sizeof(BinaryRecord) == 48, "Binary record layout changed unexpectedly.");

inline BinaryRecord to_record(const Message& message) {
    return BinaryRecord{
        .source_id = message.source_id,
        .sequence = message.sequence,
        .event_time_ns = message.event_time_ns,
        .ingest_time_ns = message.ingest_time_ns,
        .value = message.value,
        .kind = static_cast<std::uint8_t>(message.kind),
        .valid = message.valid,
        .reserved = message.reserved
    };
}

}  // namespace daq
