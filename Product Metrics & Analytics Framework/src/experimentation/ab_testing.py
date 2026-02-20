"""
A/B Testing Framework.

Implements:
- Frequentist: z-test for proportions, t-test for continuous, chi-squared
- Bayesian: Beta-Binomial posterior, probability of being best
- Sequential testing: O'Brien-Fleming boundaries
- Power analysis and sample size calculation
- Multiple testing correction (Bonferroni, Holm)
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class ABTestResult:
    metric_name: str
    control_mean: float
    treatment_mean: float
    absolute_lift: float
    relative_lift_pct: float
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    method: str
    n_control: int
    n_treatment: int
    power: float


@dataclass
class BayesianResult:
    metric_name: str
    control_mean: float
    treatment_mean: float
    prob_treatment_better: float
    expected_loss_control: float    # Expected loss if we choose control
    expected_loss_treatment: float  # Expected loss if we choose treatment
    credible_interval: Tuple[float, float]  # 95% credible interval of lift
    n_samples: int


@dataclass
class SequentialResult:
    look_number: int
    z_statistic: float
    boundary: float
    reject_null: bool
    adjusted_alpha: float
    cumulative_n: int


@dataclass
class PowerAnalysis:
    sample_size_per_group: int
    baseline_rate: float
    min_detectable_effect: float
    alpha: float
    power: float
    duration_days: int           # Estimated experiment duration


class FrequentistTester:
    """Frequentist A/B testing with multiple testing correction."""

    def test_proportion(
        self, control: np.ndarray, treatment: np.ndarray,
        metric_name: str = "conversion", alpha: float = 0.05,
    ) -> ABTestResult:
        """Two-proportion z-test for binary outcomes."""
        n_c, n_t = len(control), len(treatment)
        p_c = control.mean()
        p_t = treatment.mean()

        # Pooled proportion
        p_pool = (control.sum() + treatment.sum()) / (n_c + n_t)
        se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))

        if se == 0:
            z = 0
            p_val = 1.0
        else:
            z = (p_t - p_c) / se
            p_val = 2 * (1 - stats.norm.cdf(abs(z)))

        # CI for difference
        se_diff = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
        ci = (round(p_t - p_c - 1.96 * se_diff, 6), round(p_t - p_c + 1.96 * se_diff, 6))

        lift = p_t - p_c
        rel_lift = lift / p_c * 100 if p_c > 0 else 0

        power = self._compute_power(n_c, p_c, abs(lift), alpha)

        return ABTestResult(
            metric_name=metric_name, control_mean=round(p_c, 6),
            treatment_mean=round(p_t, 6), absolute_lift=round(lift, 6),
            relative_lift_pct=round(rel_lift, 2), p_value=round(p_val, 6),
            confidence_interval=ci, is_significant=p_val < alpha,
            method="z-test (proportions)", n_control=n_c, n_treatment=n_t,
            power=round(power, 4),
        )

    def test_continuous(
        self, control: np.ndarray, treatment: np.ndarray,
        metric_name: str = "revenue", alpha: float = 0.05,
    ) -> ABTestResult:
        """Welch's t-test for continuous outcomes."""
        n_c, n_t = len(control), len(treatment)
        m_c, m_t = control.mean(), treatment.mean()

        t_stat, p_val = stats.ttest_ind(treatment, control, equal_var=False)

        se_diff = np.sqrt(control.var() / n_c + treatment.var() / n_t)
        ci = (round(m_t - m_c - 1.96 * se_diff, 4), round(m_t - m_c + 1.96 * se_diff, 4))

        lift = m_t - m_c
        rel_lift = lift / m_c * 100 if m_c > 0 else 0

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((control.var() * (n_c - 1) + treatment.var() * (n_t - 1)) / (n_c + n_t - 2))
        d = lift / pooled_std if pooled_std > 0 else 0

        return ABTestResult(
            metric_name=metric_name, control_mean=round(m_c, 4),
            treatment_mean=round(m_t, 4), absolute_lift=round(lift, 4),
            relative_lift_pct=round(rel_lift, 2), p_value=round(p_val, 6),
            confidence_interval=ci, is_significant=p_val < alpha,
            method="Welch's t-test", n_control=n_c, n_treatment=n_t,
            power=round(min(1.0, abs(d) * np.sqrt(n_c / 2)), 4),
        )

    @staticmethod
    def _compute_power(n: int, p0: float, delta: float, alpha: float) -> float:
        """Compute statistical power for proportion test."""
        if delta == 0 or p0 == 0:
            return 0
        p1 = p0 + delta
        se0 = np.sqrt(2 * p0 * (1 - p0) / n)
        se1 = np.sqrt(p0 * (1 - p0) / n + p1 * (1 - p1) / n)
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_power = (abs(delta) - z_alpha * se0) / se1
        return float(stats.norm.cdf(z_power))

    @staticmethod
    def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
        """Apply Bonferroni correction for multiple testing."""
        m = len(p_values)
        adjusted_alpha = alpha / m
        return [(p, p < adjusted_alpha) for p in p_values]

    @staticmethod
    def holm_correction(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, bool]]:
        """Apply Holm-Bonferroni step-down correction."""
        m = len(p_values)
        sorted_idx = np.argsort(p_values)
        results = [None] * m

        for rank, idx in enumerate(sorted_idx):
            threshold = alpha / (m - rank)
            results[idx] = (p_values[idx], p_values[idx] < threshold)

        return results


class BayesianTester:
    """Bayesian A/B testing with Beta-Binomial model."""

    def __init__(self, prior_a: float = 1.0, prior_b: float = 1.0):
        self.prior_a = prior_a
        self.prior_b = prior_b

    def test_proportion(
        self, control: np.ndarray, treatment: np.ndarray,
        metric_name: str = "conversion", n_sim: int = 100000,
    ) -> BayesianResult:
        """Bayesian test using Beta posterior for proportions."""
        # Posterior parameters
        a_c = self.prior_a + control.sum()
        b_c = self.prior_b + len(control) - control.sum()
        a_t = self.prior_a + treatment.sum()
        b_t = self.prior_b + len(treatment) - treatment.sum()

        # Monte Carlo simulation
        samples_c = np.random.beta(a_c, b_c, n_sim)
        samples_t = np.random.beta(a_t, b_t, n_sim)

        prob_t_better = (samples_t > samples_c).mean()

        # Expected loss
        lift = samples_t - samples_c
        loss_control = np.maximum(lift, 0).mean()      # Loss if we pick control
        loss_treatment = np.maximum(-lift, 0).mean()    # Loss if we pick treatment

        # 95% credible interval of lift
        ci = (round(np.percentile(lift, 2.5), 6), round(np.percentile(lift, 97.5), 6))

        return BayesianResult(
            metric_name=metric_name,
            control_mean=round(control.mean(), 6),
            treatment_mean=round(treatment.mean(), 6),
            prob_treatment_better=round(prob_t_better, 4),
            expected_loss_control=round(loss_control, 6),
            expected_loss_treatment=round(loss_treatment, 6),
            credible_interval=ci,
            n_samples=n_sim,
        )


class SequentialTester:
    """Sequential testing with O'Brien-Fleming spending function."""

    @staticmethod
    def compute_boundaries(n_looks: int, alpha: float = 0.05) -> List[float]:
        """Compute O'Brien-Fleming-like boundaries for sequential testing."""
        boundaries = []
        for k in range(1, n_looks + 1):
            info_frac = k / n_looks
            z_bound = stats.norm.ppf(1 - alpha / 2) / np.sqrt(info_frac)
            boundaries.append(round(z_bound, 4))
        return boundaries

    def sequential_test(
        self, control: np.ndarray, treatment: np.ndarray,
        n_looks: int = 5, alpha: float = 0.05,
    ) -> List[SequentialResult]:
        """Run sequential test with interim analyses."""
        n = min(len(control), len(treatment))
        boundaries = self.compute_boundaries(n_looks, alpha)
        look_size = n // n_looks
        results = []

        for k in range(1, n_looks + 1):
            end = k * look_size
            c_k = control[:end]
            t_k = treatment[:end]

            p_c = c_k.mean()
            p_t = t_k.mean()
            p_pool = (c_k.sum() + t_k.sum()) / (2 * end)
            se = np.sqrt(p_pool * (1 - p_pool) * 2 / end) if p_pool > 0 else 1

            z = (p_t - p_c) / se if se > 0 else 0

            results.append(SequentialResult(
                look_number=k, z_statistic=round(z, 4),
                boundary=boundaries[k - 1],
                reject_null=abs(z) > boundaries[k - 1],
                adjusted_alpha=round(alpha * (k / n_looks), 6),
                cumulative_n=2 * end,
            ))

        return results


class PowerCalculator:
    """Sample size and power calculations."""

    @staticmethod
    def sample_size_proportion(
        baseline_rate: float, mde: float,
        alpha: float = 0.05, power: float = 0.80,
    ) -> int:
        """Minimum sample size per group for proportion test."""
        p1 = baseline_rate
        p2 = baseline_rate + mde
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)

        n = ((z_alpha * np.sqrt(2 * p1 * (1 - p1)) +
              z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / mde) ** 2

        return int(np.ceil(n))

    @staticmethod
    def estimate_duration(
        sample_per_group: int, daily_traffic: int, allocation: float = 0.50,
    ) -> int:
        """Estimate experiment duration in days."""
        daily_per_group = daily_traffic * allocation
        if daily_per_group <= 0:
            return 999
        return int(np.ceil(sample_per_group / daily_per_group))
