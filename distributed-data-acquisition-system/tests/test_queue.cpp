#include "core/spsc_queue.hpp"

#include <cassert>
#include <iostream>
#include <thread>
#include <vector>

int main() {
    daq::SpscQueue<int> queue(8);
    assert(queue.capacity() == 8);
    assert(queue.push(1));
    assert(queue.push(2));
    auto first = queue.pop();
    auto second = queue.pop();
    assert(first.has_value() && first.value() == 1);
    assert(second.has_value() && second.value() == 2);

    daq::SpscQueue<int> threaded_queue(1024);
    std::vector<int> values;
    values.reserve(1000);

    std::thread producer([&]() {
        for (int i = 0; i < 1000; ++i) {
            while (!threaded_queue.push(i)) {}
        }
    });

    std::thread consumer([&]() {
        while (values.size() < 1000) {
            auto item = threaded_queue.pop();
            if (item.has_value()) {
                values.push_back(item.value());
            }
        }
    });

    producer.join();
    consumer.join();

    assert(values.front() == 0);
    assert(values.back() == 999);
    std::cout << "queue test passed\n";
    return 0;
}
