#pragma once

#include <cstdint>
#include <string>

namespace llmde::io {

class UdpPublisher {
  public:
    UdpPublisher(std::string host, std::uint16_t port);
    ~UdpPublisher();

    UdpPublisher(const UdpPublisher&) = delete;
    UdpPublisher& operator=(const UdpPublisher&) = delete;
    UdpPublisher(UdpPublisher&& other) noexcept;
    UdpPublisher& operator=(UdpPublisher&& other) noexcept;

    void publish(const std::string& payload) const;

  private:
    int socket_fd_{-1};
    std::string host_;
    std::uint16_t port_{};
};

}  // namespace llmde::io
