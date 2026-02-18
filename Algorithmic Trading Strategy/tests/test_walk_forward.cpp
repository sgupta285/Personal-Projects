#include "test_framework.h"
#include "utils/walk_forward.h"

using namespace bt;

TEST(walk_forward_window_generation) {
    auto windows = WalkForwardValidator::generate_windows(2520, 504, 126, 63);

    ASSERT_GT(static_cast<int>(windows.size()), 0);

    // Each window should have non-overlapping train/test
    for (const auto& w : windows) {
        ASSERT_TRUE(w.train_end < w.test_start);
        ASSERT_TRUE(w.train_start < w.train_end);
        ASSERT_TRUE(w.test_start <= w.test_end);
    }

    // Windows should be sequential
    for (size_t i = 1; i < windows.size(); ++i) {
        ASSERT_TRUE(windows[i].train_start > windows[i-1].train_start);
    }
}

TEST(walk_forward_window_sizes) {
    auto windows = WalkForwardValidator::generate_windows(2520, 504, 126, 63);

    for (const auto& w : windows) {
        int train_size = w.train_end - w.train_start + 1;
        int test_size = w.test_end - w.test_start + 1;
        ASSERT_EQ(train_size, 504);
        ASSERT_TRUE(test_size > 0);
        ASSERT_TRUE(test_size <= 126);
    }
}

TEST(walk_forward_no_windows_for_short_data) {
    auto windows = WalkForwardValidator::generate_windows(100, 504, 126, 63);
    ASSERT_EQ(static_cast<int>(windows.size()), 0);
}
