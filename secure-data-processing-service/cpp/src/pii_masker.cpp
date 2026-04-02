#include <iostream>
#include <regex>
#include <sstream>
#include <string>

int main() {
    std::ostringstream buffer;
    buffer << std::cin.rdbuf();
    std::string input = buffer.str();

    std::regex email_pattern(R"(([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,}))");
    std::regex digits_pattern(R"(\b\d{3}[- ]?\d{2}[- ]?\d{4}\b)");

    std::string masked = std::regex_replace(input, email_pattern, "redacted@example.com");
    masked = std::regex_replace(masked, digits_pattern, "***-**-****");

    std::cout << masked;
    return 0;
}
