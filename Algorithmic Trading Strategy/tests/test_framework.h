/**
 * Minimal test framework (no external dependencies needed).
 */

#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <cmath>
#include <sstream>

namespace test {

struct TestCase {
    std::string name;
    std::function<void()> fn;
};

inline std::vector<TestCase>& registry() {
    static std::vector<TestCase> cases;
    return cases;
}

inline int& fail_count() {
    static int count = 0;
    return count;
}

inline int& pass_count() {
    static int count = 0;
    return count;
}

struct Registrar {
    Registrar(const std::string& name, std::function<void()> fn) {
        registry().push_back({name, std::move(fn)});
    }
};

inline void assert_true(bool cond, const std::string& msg, const char* file, int line) {
    if (!cond) {
        std::cerr << "  FAIL: " << msg << " at " << file << ":" << line << "\n";
        fail_count()++;
    } else {
        pass_count()++;
    }
}

inline void assert_near(double actual, double expected, double tol, const std::string& msg, const char* file, int line) {
    if (std::abs(actual - expected) > tol) {
        std::cerr << "  FAIL: " << msg << " (expected " << expected << ", got " << actual
                  << ", tol " << tol << ") at " << file << ":" << line << "\n";
        fail_count()++;
    } else {
        pass_count()++;
    }
}

inline int run_all() {
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "RUNNING " << registry().size() << " TESTS\n";
    std::cout << std::string(60, '=') << "\n\n";

    for (auto& tc : registry()) {
        std::cout << "▶ " << tc.name << "... ";
        int before_fails = fail_count();
        try {
            tc.fn();
        } catch (const std::exception& e) {
            std::cerr << "\n  EXCEPTION: " << e.what() << "\n";
            fail_count()++;
        }
        if (fail_count() == before_fails) {
            std::cout << "✓\n";
        } else {
            std::cout << "✗\n";
        }
    }

    std::cout << "\n" << std::string(60, '-') << "\n";
    std::cout << "Results: " << pass_count() << " passed, " << fail_count() << " failed\n";
    std::cout << std::string(60, '=') << "\n\n";

    return (fail_count() > 0) ? 1 : 0;
}

} // namespace test

#define TEST(name) \
    void test_##name(); \
    test::Registrar reg_##name(#name, test_##name); \
    void test_##name()

#define ASSERT_TRUE(cond) test::assert_true(cond, #cond, __FILE__, __LINE__)
#define ASSERT_FALSE(cond) test::assert_true(!(cond), "!" #cond, __FILE__, __LINE__)
#define ASSERT_NEAR(actual, expected, tol) test::assert_near(actual, expected, tol, #actual " ≈ " #expected, __FILE__, __LINE__)
#define ASSERT_GT(a, b) test::assert_true((a) > (b), #a " > " #b, __FILE__, __LINE__)
#define ASSERT_LT(a, b) test::assert_true((a) < (b), #a " < " #b, __FILE__, __LINE__)
#define ASSERT_EQ(a, b) test::assert_true((a) == (b), #a " == " #b, __FILE__, __LINE__)
