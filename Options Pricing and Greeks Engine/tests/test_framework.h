#pragma once
#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <cmath>

namespace test {
struct TestCase { std::string name; std::function<void()> fn; };
inline std::vector<TestCase>& registry() { static std::vector<TestCase> c; return c; }
inline int& fail_count() { static int c = 0; return c; }
inline int& pass_count() { static int c = 0; return c; }
struct Registrar { Registrar(const std::string& n, std::function<void()> f) { registry().push_back({n, std::move(f)}); }};
inline void assert_true(bool c, const std::string& m, const char* f, int l) { if(!c){std::cerr<<"  FAIL: "<<m<<" at "<<f<<":"<<l<<"\n";fail_count()++;}else{pass_count()++;}}
inline void assert_near(double a, double e, double t, const std::string& m, const char* f, int l) { if(std::abs(a-e)>t){std::cerr<<"  FAIL: "<<m<<" (exp "<<e<<", got "<<a<<") at "<<f<<":"<<l<<"\n";fail_count()++;}else{pass_count()++;}}
inline int run_all() { std::cout<<"\n"<<std::string(60,'=')<<"\nRUNNING "<<registry().size()<<" TESTS\n"<<std::string(60,'=')<<"\n\n"; for(auto&tc:registry()){std::cout<<"▶ "<<tc.name<<"... ";int bf=fail_count();try{tc.fn();}catch(const std::exception&e){std::cerr<<"\n  EXCEPTION: "<<e.what()<<"\n";fail_count()++;}if(fail_count()==bf)std::cout<<"✓\n";else std::cout<<"✗\n";}std::cout<<"\n"<<std::string(60,'-')<<"\n"<<pass_count()<<" passed, "<<fail_count()<<" failed\n"<<std::string(60,'=')<<"\n\n";return fail_count()>0?1:0;}
} // namespace test
#define TEST(name) void test_##name(); test::Registrar reg_##name(#name, test_##name); void test_##name()
#define ASSERT_TRUE(c) test::assert_true(c, #c, __FILE__, __LINE__)
#define ASSERT_NEAR(a, e, t) test::assert_near(a, e, t, #a " ≈ " #e, __FILE__, __LINE__)
#define ASSERT_GT(a, b) test::assert_true((a)>(b), #a " > " #b, __FILE__, __LINE__)
#define ASSERT_LT(a, b) test::assert_true((a)<(b), #a " < " #b, __FILE__, __LINE__)
