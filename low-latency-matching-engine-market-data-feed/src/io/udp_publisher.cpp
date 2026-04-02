#include "llmde/io/udp_publisher.hpp"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <stdexcept>

namespace llmde::io {

UdpPublisher::UdpPublisher(std::string host, std::uint16_t port) : host_(std::move(host)), port_(port) {
    socket_fd_ = ::socket(AF_INET, SOCK_DGRAM, 0);
}

UdpPublisher::~UdpPublisher() {
    if (socket_fd_ >= 0) {
        ::close(socket_fd_);
    }
}

UdpPublisher::UdpPublisher(UdpPublisher&& other) noexcept : socket_fd_(other.socket_fd_), host_(std::move(other.host_)), port_(other.port_) {
    other.socket_fd_ = -1;
}

UdpPublisher& UdpPublisher::operator=(UdpPublisher&& other) noexcept {
    if (this != &other) {
        if (socket_fd_ >= 0) {
            ::close(socket_fd_);
        }
        socket_fd_ = other.socket_fd_;
        host_ = std::move(other.host_);
        port_ = other.port_;
        other.socket_fd_ = -1;
    }
    return *this;
}

void UdpPublisher::publish(const std::string& payload) const {
    if (socket_fd_ < 0) {
        return;
    }
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port_);
    ::inet_pton(AF_INET, host_.c_str(), &addr.sin_addr);
    ::sendto(socket_fd_, payload.data(), payload.size(), 0, reinterpret_cast<const sockaddr*>(&addr), sizeof(addr));
}

}  // namespace llmde::io
