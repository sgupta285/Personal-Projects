#include "test_framework.h"
#include "engine/portfolio.h"

using namespace bt;

TEST(portfolio_initial_state) {
    Portfolio p(1'000'000.0);
    ASSERT_NEAR(p.cash(), 1'000'000.0, 0.01);
    ASSERT_EQ(p.num_positions(), 0);
}

TEST(portfolio_buy_and_sell) {
    Portfolio p(100'000.0);
    std::unordered_map<std::string, double> prices = {{"AAPL", 150.0}};

    // Buy 100 shares at $150
    Order buy_order;
    buy_order.symbol = "AAPL";
    buy_order.side = Order::Side::BUY;
    buy_order.type = Order::Type::MARKET;
    buy_order.quantity = 100;
    buy_order.timestamp = 0;

    auto fill = p.execute_fill(buy_order, 150.0, 0.0, 10.0);
    ASSERT_EQ(fill.quantity, 100);
    ASSERT_NEAR(p.cash(), 100'000.0 - 150.0 * 100 - 10.0, 0.01);
    ASSERT_TRUE(p.has_position("AAPL"));
    ASSERT_EQ(p.get_position("AAPL").quantity, 100);

    // Sell 50 shares at $160
    Order sell_order;
    sell_order.symbol = "AAPL";
    sell_order.side = Order::Side::SELL;
    sell_order.type = Order::Type::MARKET;
    sell_order.quantity = 50;
    sell_order.timestamp = 1;

    auto sell_fill = p.execute_fill(sell_order, 160.0, 0.0, 10.0);
    ASSERT_EQ(p.get_position("AAPL").quantity, 50);

    // Equity should reflect partial sale
    prices["AAPL"] = 160.0;
    double eq = p.equity(prices);
    ASSERT_GT(eq, 100'000.0); // Profit from price increase
}

TEST(portfolio_full_close) {
    Portfolio p(50'000.0);

    Order buy = {"SYM1", Order::Side::BUY, Order::Type::MARKET, 100, 0, 0};
    p.execute_fill(buy, 100.0, 0.0, 0.0);
    ASSERT_TRUE(p.has_position("SYM1"));

    Order sell = {"SYM1", Order::Side::SELL, Order::Type::MARKET, 100, 0, 0};
    p.execute_fill(sell, 110.0, 0.0, 0.0);
    ASSERT_FALSE(p.has_position("SYM1"));
    ASSERT_EQ(p.num_positions(), 0);
}

TEST(portfolio_reset) {
    Portfolio p(100'000.0);
    Order buy = {"TEST", Order::Side::BUY, Order::Type::MARKET, 10, 0, 0};
    p.execute_fill(buy, 50.0, 0.0, 0.0);

    p.reset(200'000.0);
    ASSERT_NEAR(p.cash(), 200'000.0, 0.01);
    ASSERT_EQ(p.num_positions(), 0);
}
