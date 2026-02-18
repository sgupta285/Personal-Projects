#pragma once

#include "engine/types.h"
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

#ifdef USE_AVX2
#include <immintrin.h>
#endif

namespace bt {

class MetricsCalculator {
public:
    static PerformanceMetrics compute(
        const std::vector<PortfolioSnapshot>& snapshots,
        const std::vector<TradeRecord>& trades,
        const std::vector<double>& benchmark_returns,
        double risk_free_rate = 0.04
    ) {
        PerformanceMetrics m{};
        if (snapshots.size() < 2) return m;

        // Extract daily returns
        std::vector<double> returns;
        returns.reserve(snapshots.size());
        for (size_t i = 1; i < snapshots.size(); ++i) {
            returns.push_back(snapshots[i].daily_return);
        }

        int n = static_cast<int>(returns.size());
        double daily_rf = risk_free_rate / 252.0;

        // Basic stats
        double sum = vector_sum(returns);
        double mean_ret = sum / n;
        double total_ret = snapshots.back().equity / snapshots.front().equity - 1.0;
        double years = n / 252.0;

        m.total_return = total_ret;
        m.annualized_return = std::pow(1.0 + total_ret, 1.0 / years) - 1.0;

        // Volatility
        double var = 0.0;
        for (double r : returns) var += (r - mean_ret) * (r - mean_ret);
        var /= (n - 1);
        m.annualized_volatility = std::sqrt(var * 252.0);

        // Sharpe
        double excess_mean = mean_ret - daily_rf;
        double daily_vol = std::sqrt(var);
        m.sharpe_ratio = (daily_vol > 0.0) ? (excess_mean / daily_vol) * std::sqrt(252.0) : 0.0;

        // Sortino
        double downside_var = 0.0;
        int down_count = 0;
        for (double r : returns) {
            if (r < daily_rf) {
                downside_var += (r - daily_rf) * (r - daily_rf);
                down_count++;
            }
        }
        m.downside_deviation = (down_count > 0) ? std::sqrt(downside_var / down_count * 252.0) : 0.0;
        m.sortino_ratio = (m.downside_deviation > 0.0) ?
            (m.annualized_return - risk_free_rate) / m.downside_deviation : 0.0;

        // Max drawdown
        double peak = snapshots[0].equity;
        double max_dd = 0.0;
        double dd_start_peak = peak;
        int dd_start = 0, max_dd_duration = 0, current_dd_start = 0;

        for (size_t i = 1; i < snapshots.size(); ++i) {
            double eq = snapshots[i].equity;
            if (eq > peak) {
                int duration = static_cast<int>(i) - current_dd_start;
                if (duration > max_dd_duration) max_dd_duration = duration;
                peak = eq;
                current_dd_start = static_cast<int>(i);
            }
            double dd = 1.0 - (eq / peak);
            if (dd > max_dd) max_dd = dd;
        }
        m.max_drawdown = max_dd;
        m.max_drawdown_duration_days = max_dd_duration;
        m.calmar_ratio = (max_dd > 0.0) ? m.annualized_return / max_dd : 0.0;

        // Higher moments
        double m3 = 0.0, m4 = 0.0;
        for (double r : returns) {
            double z = (r - mean_ret) / daily_vol;
            m3 += z * z * z;
            m4 += z * z * z * z;
        }
        m.skewness = m3 / n;
        m.kurtosis = m4 / n - 3.0; // Excess kurtosis

        // VaR and CVaR (95%)
        std::vector<double> sorted_returns = returns;
        std::sort(sorted_returns.begin(), sorted_returns.end());
        int var_idx = static_cast<int>(std::floor(0.05 * n));
        m.var_95 = -sorted_returns[var_idx];
        double cvar_sum = 0.0;
        for (int i = 0; i <= var_idx; ++i) cvar_sum += sorted_returns[i];
        m.cvar_95 = -(cvar_sum / (var_idx + 1));

        // Trade metrics
        m.total_trades = static_cast<int>(trades.size());
        m.winning_trades = 0;
        m.losing_trades = 0;
        double win_sum = 0.0, loss_sum = 0.0;

        for (const auto& t : trades) {
            if (t.pnl > 0) {
                m.winning_trades++;
                win_sum += t.pnl;
            } else {
                m.losing_trades++;
                loss_sum += std::abs(t.pnl);
            }
        }

        m.win_rate = (m.total_trades > 0) ? static_cast<double>(m.winning_trades) / m.total_trades : 0.0;
        m.profit_factor = (loss_sum > 0.0) ? win_sum / loss_sum : (win_sum > 0 ? 999.0 : 0.0);
        m.avg_trade_return = (m.total_trades > 0) ?
            std::accumulate(trades.begin(), trades.end(), 0.0,
                [](double s, const TradeRecord& t) { return s + t.return_pct; }) / m.total_trades : 0.0;
        m.avg_winner = (m.winning_trades > 0) ? win_sum / m.winning_trades : 0.0;
        m.avg_loser = (m.losing_trades > 0) ? loss_sum / m.losing_trades : 0.0;

        // Alpha/Beta vs benchmark
        if (!benchmark_returns.empty()) {
            int bm_n = std::min(n, static_cast<int>(benchmark_returns.size()));
            double bm_mean = 0.0;
            for (int i = 0; i < bm_n; ++i) bm_mean += benchmark_returns[i];
            bm_mean /= bm_n;

            double cov = 0.0, bm_var = 0.0;
            for (int i = 0; i < bm_n; ++i) {
                cov += (returns[i] - mean_ret) * (benchmark_returns[i] - bm_mean);
                bm_var += (benchmark_returns[i] - bm_mean) * (benchmark_returns[i] - bm_mean);
            }
            cov /= (bm_n - 1);
            bm_var /= (bm_n - 1);

            m.beta = (bm_var > 0.0) ? cov / bm_var : 0.0;
            m.alpha = (m.annualized_return - risk_free_rate) - m.beta * (bm_mean * 252.0 - risk_free_rate);

            // Tracking error / information ratio
            double te_var = 0.0;
            for (int i = 0; i < bm_n; ++i) {
                double diff = returns[i] - benchmark_returns[i];
                te_var += diff * diff;
            }
            double te = std::sqrt(te_var / (bm_n - 1) * 252.0);
            m.information_ratio = (te > 0.0) ? (m.annualized_return - bm_mean * 252.0) / te : 0.0;
        }

        // Turnover (approximate)
        double total_traded = 0.0;
        for (const auto& t : trades) {
            total_traded += std::abs(t.entry_price * t.quantity);
        }
        double avg_equity = (snapshots.front().equity + snapshots.back().equity) / 2.0;
        m.turnover = (avg_equity > 0.0 && years > 0.0) ? (total_traded / avg_equity) / years : 0.0;

        return m;
    }

private:
    static double vector_sum(const std::vector<double>& v) {
#ifdef USE_AVX2
        // SIMD-accelerated sum
        size_t n = v.size();
        size_t simd_end = (n / 4) * 4;
        __m256d acc = _mm256_setzero_pd();

        for (size_t i = 0; i < simd_end; i += 4) {
            __m256d vals = _mm256_loadu_pd(&v[i]);
            acc = _mm256_add_pd(acc, vals);
        }

        double result[4];
        _mm256_storeu_pd(result, acc);
        double sum = result[0] + result[1] + result[2] + result[3];

        for (size_t i = simd_end; i < n; ++i) sum += v[i];
        return sum;
#else
        double sum = 0.0;
        for (double x : v) sum += x;
        return sum;
#endif
    }
};

} // namespace bt
