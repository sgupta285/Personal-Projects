#pragma once

#include <cmath>
#include <algorithm>

#ifdef USE_AVX2
#include <immintrin.h>
#endif

namespace opt {

// Abramowitz & Stegun approximation for standard normal CDF
// Max error: 7.5e-8
inline double norm_cdf(double x) {
    if (x > 8.0) return 1.0;
    if (x < -8.0) return 0.0;

    constexpr double a1 =  0.254829592;
    constexpr double a2 = -0.284496736;
    constexpr double a3 =  1.421413741;
    constexpr double a4 = -1.453152027;
    constexpr double a5 =  1.061405429;
    constexpr double p  =  0.3275911;

    double sign = (x >= 0.0) ? 1.0 : -1.0;
    x = std::abs(x) / std::sqrt(2.0);

    double t = 1.0 / (1.0 + p * x);
    double y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * std::exp(-x * x);

    return 0.5 * (1.0 + sign * y);
}

// Standard normal PDF
inline double norm_pdf(double x) {
    constexpr double inv_sqrt_2pi = 0.3989422804014327;
    return inv_sqrt_2pi * std::exp(-0.5 * x * x);
}

// Inverse normal CDF (Beasley-Springer-Moro approximation)
inline double norm_inv(double u) {
    if (u <= 0.0) return -8.0;
    if (u >= 1.0) return 8.0;

    static const double a[] = {
        -3.969683028665376e+01, 2.209460984245205e+02,
        -2.759285104469687e+02, 1.383577518672690e+02,
        -3.066479806614716e+01, 2.506628277459239e+00
    };
    static const double b[] = {
        -5.447609879822406e+01, 1.615858368580409e+02,
        -1.556989798598866e+02, 6.680131188771972e+01,
        -1.328068155288572e+01
    };
    static const double c[] = {
        -7.784894002430293e-03, -3.223964580411365e-01,
        -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00,  2.938163982698783e+00
    };
    static const double d[] = {
         7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00
    };

    double q, r;
    if (u < 0.02425) {
        q = std::sqrt(-2.0 * std::log(u));
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
    } else if (u <= 0.97575) {
        q = u - 0.5;
        r = q * q;
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q /
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
    } else {
        q = std::sqrt(-2.0 * std::log(1.0 - u));
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
    }
}

#ifdef USE_AVX2
// Vectorized norm_cdf for 4 doubles at once
inline __m256d norm_cdf_avx2(__m256d x) {
    // Simplified polynomial approximation for vectorized use
    __m256d zero = _mm256_setzero_pd();
    __m256d one = _mm256_set1_pd(1.0);
    __m256d half = _mm256_set1_pd(0.5);
    __m256d p = _mm256_set1_pd(0.3275911);

    __m256d sign = _mm256_blendv_pd(_mm256_set1_pd(-1.0), one, _mm256_cmp_pd(x, zero, _CMP_GE_OQ));
    __m256d abs_x = _mm256_div_pd(
        _mm256_andnot_pd(_mm256_set1_pd(-0.0), x),
        _mm256_set1_pd(std::sqrt(2.0))
    );

    __m256d t = _mm256_div_pd(one, _mm256_fmadd_pd(p, abs_x, one));

    __m256d a1 = _mm256_set1_pd(0.254829592);
    __m256d a2 = _mm256_set1_pd(-0.284496736);
    __m256d a3 = _mm256_set1_pd(1.421413741);
    __m256d a4 = _mm256_set1_pd(-1.453152027);
    __m256d a5 = _mm256_set1_pd(1.061405429);

    // Horner's method: ((((a5*t + a4)*t + a3)*t + a2)*t + a1)*t
    __m256d poly = _mm256_fmadd_pd(a5, t, a4);
    poly = _mm256_fmadd_pd(poly, t, a3);
    poly = _mm256_fmadd_pd(poly, t, a2);
    poly = _mm256_fmadd_pd(poly, t, a1);
    poly = _mm256_mul_pd(poly, t);

    // exp(-x^2)
    __m256d neg_x_sq = _mm256_mul_pd(abs_x, abs_x);
    neg_x_sq = _mm256_sub_pd(zero, neg_x_sq);
    // Approximate exp via scalar fallback
    double vals[4], exp_vals[4];
    _mm256_storeu_pd(vals, neg_x_sq);
    for (int i = 0; i < 4; ++i) exp_vals[i] = std::exp(vals[i]);
    __m256d exp_v = _mm256_loadu_pd(exp_vals);

    __m256d y = _mm256_sub_pd(one, _mm256_mul_pd(poly, exp_v));

    return _mm256_fmadd_pd(half, _mm256_mul_pd(sign, y), half);
}
#endif

} // namespace opt
