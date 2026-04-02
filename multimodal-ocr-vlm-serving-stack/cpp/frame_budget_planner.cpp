#include <cmath>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cerr << "usage: frame_budget_planner <width> <height> <pages>\n";
        return 1;
    }
    const double width = std::stod(argv[1]);
    const double height = std::stod(argv[2]);
    const double pages = std::stod(argv[3]);
    const double pixels = width * height * std::max(1.0, pages);
    const double tile_count = std::ceil(pixels / 900000.0);
    const double estimated_memory_mb = std::max(64.0, tile_count * 96.0);
    std::cout << "{\n"
              << "  \"tile_count\": " << tile_count << ",\n"
              << "  \"estimated_memory_mb\": " << estimated_memory_mb << "\n"
              << "}\n";
    return 0;
}
