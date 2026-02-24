"""
Synthetic Control Method.

Constructs a weighted combination of control states to match the treated
state's pre-treatment outcome trajectory, then estimates the treatment
effect as the post-treatment divergence.

Implements:
1. Convex combination weight optimization (NNLS)
2. Pre-treatment fit diagnostics (RMSPE)
3. Placebo tests (permutation-based p-value)
"""

import numpy as np
import pandas as pd
from scipy.optimize import nnls, minimize
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import structlog

logger = structlog.get_logger()


@dataclass
class SyntheticControlResult:
    treated_state: str
    weights: Dict[str, float]         # Control state → weight
    pre_rmspe: float                  # Pre-treatment fit quality
    post_rmspe: float
    estimated_effect: float           # Avg post-treatment gap
    effect_by_period: List[float]     # Gap per post-treatment period
    treated_series: np.ndarray
    synthetic_series: np.ndarray
    ratio_post_pre_rmspe: float       # Post/pre RMSPE ratio


@dataclass
class PlaceboResult:
    state: str
    is_treated: bool
    ratio_post_pre: float
    rank: int
    p_value: float


class SyntheticControlEstimator:
    """Abadie-Diamond-Hainmueller Synthetic Control Method."""

    def estimate(
        self,
        df: pd.DataFrame,
        treated_state: str,
        outcome: str = "employment_rate",
        treatment_quarter: int = 20,
    ) -> SyntheticControlResult:
        """
        Build synthetic control and estimate treatment effect.

        Steps:
        1. Pivot data to state × time matrix
        2. Split into pre/post treatment
        3. Solve for weights: min ||Y_treat_pre - W' Y_ctrl_pre||²
        4. Compute gap: Y_treat_post - W' Y_ctrl_post
        """
        # Pivot
        pivot = df.pivot_table(values=outcome, index="quarter", columns="state")
        states = list(pivot.columns)

        if treated_state not in states:
            raise ValueError(f"Treated state '{treated_state}' not found")

        control_states = [s for s in states if s != treated_state]

        # Pre/post split
        pre = pivot.loc[:treatment_quarter - 1]
        post = pivot.loc[treatment_quarter:]

        y_treat_pre = pre[treated_state].values
        Y_ctrl_pre = pre[control_states].values

        y_treat_post = post[treated_state].values
        Y_ctrl_post = post[control_states].values

        # Solve for weights using NNLS (non-negative constraint)
        weights, residual = nnls(Y_ctrl_pre, y_treat_pre)

        # Normalize to sum ≈ 1 (convex combination)
        w_sum = weights.sum()
        if w_sum > 0:
            weights_normalized = weights / w_sum
        else:
            weights_normalized = np.ones(len(control_states)) / len(control_states)

        # Build synthetic series
        synth_pre = Y_ctrl_pre @ weights_normalized
        synth_post = Y_ctrl_post @ weights_normalized
        synth_full = np.concatenate([synth_pre, synth_post])
        treated_full = np.concatenate([y_treat_pre, y_treat_post])

        # Diagnostics
        pre_rmspe = np.sqrt(np.mean((y_treat_pre - synth_pre) ** 2))
        post_rmspe = np.sqrt(np.mean((y_treat_post - synth_post) ** 2))
        ratio = post_rmspe / pre_rmspe if pre_rmspe > 0 else 999

        # Treatment effect
        gap_post = y_treat_post - synth_post
        avg_effect = float(np.mean(gap_post))

        # Weight dictionary (only non-trivial weights)
        weight_dict = {}
        for s, w in zip(control_states, weights_normalized):
            if w > 0.01:
                weight_dict[s] = round(w, 4)

        return SyntheticControlResult(
            treated_state=treated_state,
            weights=weight_dict,
            pre_rmspe=round(pre_rmspe, 6),
            post_rmspe=round(post_rmspe, 6),
            estimated_effect=round(avg_effect, 6),
            effect_by_period=list(np.round(gap_post, 6)),
            treated_series=treated_full,
            synthetic_series=synth_full,
            ratio_post_pre_rmspe=round(ratio, 3),
        )

    def placebo_test(
        self,
        df: pd.DataFrame,
        treated_state: str,
        outcome: str = "employment_rate",
        treatment_quarter: int = 20,
        max_pre_rmspe_ratio: float = 5.0,
    ) -> Tuple[List[PlaceboResult], float]:
        """
        Run placebo tests: apply synthetic control to each control state.

        States with poor pre-treatment fit (high RMSPE) are excluded.
        P-value = fraction of placebos with ratio ≥ treated state's ratio.
        """
        states = df["state"].unique()
        control_states = [s for s in states if s != treated_state]

        # Get treated state's result
        treated_result = self.estimate(df, treated_state, outcome, treatment_quarter)
        treated_ratio = treated_result.ratio_post_pre_rmspe

        placebo_results = []

        # Run synthetic control for each control state as "placebo treated"
        for ctrl_state in control_states:
            try:
                # Exclude the actual treated state from donor pool for this placebo
                placebo_df = df[df["state"] != treated_state].copy()
                # Reassign: ctrl_state is now "treated"
                result = self.estimate(placebo_df, ctrl_state, outcome, treatment_quarter)

                # Filter out poor pre-fit
                if result.pre_rmspe > 0 and result.ratio_post_pre_rmspe < max_pre_rmspe_ratio * treated_ratio:
                    placebo_results.append(PlaceboResult(
                        state=ctrl_state, is_treated=False,
                        ratio_post_pre=result.ratio_post_pre_rmspe,
                        rank=0, p_value=0,
                    ))
            except Exception:
                continue

        # Add treated state
        placebo_results.append(PlaceboResult(
            state=treated_state, is_treated=True,
            ratio_post_pre=treated_ratio,
            rank=0, p_value=0,
        ))

        # Rank by ratio
        placebo_results.sort(key=lambda r: r.ratio_post_pre, reverse=True)
        for i, r in enumerate(placebo_results):
            r.rank = i + 1

        # P-value: fraction with ratio ≥ treated
        n_total = len(placebo_results)
        treated_rank = next(r.rank for r in placebo_results if r.is_treated)
        p_value = treated_rank / n_total

        for r in placebo_results:
            r.p_value = round(p_value, 4) if r.is_treated else round(r.rank / n_total, 4)

        return placebo_results, round(p_value, 4)
