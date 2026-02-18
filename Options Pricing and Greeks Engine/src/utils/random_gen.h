#pragma once

#include <vector>
#include <random>
#include <cmath>
#include "utils/normal_dist.h"

namespace opt {

class RandomGenerator {
public:
    // Standard pseudo-random normal samples
    static std::vector<double> generate_normals(int n, unsigned seed = 42) {
        std::mt19937_64 rng(seed);
        std::normal_distribution<double> dist(0.0, 1.0);
        std::vector<double> samples(n);
        for (int i = 0; i < n; ++i) samples[i] = dist(rng);
        return samples;
    }

    // Antithetic pairs: for each z, also use -z
    static std::vector<double> generate_antithetic(int n, unsigned seed = 42) {
        int half = n / 2;
        std::mt19937_64 rng(seed);
        std::normal_distribution<double> dist(0.0, 1.0);
        std::vector<double> samples(n);
        for (int i = 0; i < half; ++i) {
            double z = dist(rng);
            samples[2 * i] = z;
            samples[2 * i + 1] = -z;
        }
        if (n % 2 != 0) samples[n - 1] = dist(rng);
        return samples;
    }

    // Stratified sampling: divide [0,1] into n strata, sample one from each
    static std::vector<double> generate_stratified(int n, unsigned seed = 42) {
        std::mt19937_64 rng(seed);
        std::uniform_real_distribution<double> unif(0.0, 1.0);
        std::vector<double> samples(n);
        for (int i = 0; i < n; ++i) {
            double u = (i + unif(rng)) / n;
            samples[i] = norm_inv(u);
        }
        return samples;
    }

    // Sobol-like quasi-random (simplified Van der Corput sequence)
    static std::vector<double> generate_quasi_random(int n) {
        std::vector<double> samples(n);
        for (int i = 0; i < n; ++i) {
            double u = van_der_corput(i + 1, 2);
            samples[i] = norm_inv(u);
        }
        return samples;
    }

private:
    static double van_der_corput(int n, int base) {
        double result = 0.0;
        double f = 1.0 / base;
        while (n > 0) {
            result += f * (n % base);
            n /= base;
            f /= base;
        }
        return result;
    }
};

} // namespace opt
