"""
Elasticity Estimation Models.

Implements:
1. OLS Log-Log regression: ln(Q) = α + ε * ln(P) + β*X
2. Panel Fixed Effects: store + product fixed effects with clustered SE
3. IV/2SLS: Instrumental variables using supply-side cost shocks
4. Cross-price elasticity estimation via multivariate log-log
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class ElasticityResult:
    product_id: str
    method: str
    own_elasticity: float
    std_error: float
    t_statistic: float
    p_value: float
    ci_lower: float          # 95% CI lower bound
    ci_upper: float
    r_squared: float
    n_observations: int
    true_elasticity: Optional[float] = None
    estimation_error: Optional[float] = None


@dataclass
class CrossElasticityResult:
    product_i: str
    product_j: str
    cross_elasticity: float
    std_error: float
    p_value: float
    relationship: str        # "substitute", "complement", "unrelated"


@dataclass
class IVDiagnostics:
    first_stage_f: float
    instrument_relevance: str  # "strong", "weak"
    durbin_wu_hausman_p: float
    endogeneity: str           # "detected", "not_detected"
    sargan_p: Optional[float] = None


class OLSLogLogEstimator:
    """
    Standard OLS log-log regression for constant elasticity estimation.
    ln(Q) = α + ε * ln(P) + β * controls + error
    """

    def estimate(
        self, df: pd.DataFrame, product_id: str,
        controls: Optional[List[str]] = None,
        true_elasticity: Optional[float] = None,
    ) -> ElasticityResult:
        """Estimate own-price elasticity for a single product via OLS."""
        prod_data = df[df["product_id"] == product_id].copy()

        if len(prod_data) < 30:
            raise ValueError(f"Insufficient data for {product_id}: {len(prod_data)} obs")

        y = prod_data["log_quantity"].values
        X_vars = ["log_price"]

        if controls:
            X_vars.extend([c for c in controls if c in prod_data.columns])

        X = prod_data[X_vars].values
        X = sm.add_constant(X)

        model = OLS(y, X).fit(cov_type="HC1")  # Heteroskedasticity-robust SE

        # Extract own-price elasticity (coefficient on log_price)
        elasticity = model.params[1]
        se = model.bse[1]
        t_stat = model.tvalues[1]
        p_val = model.pvalues[1]
        ci = model.conf_int()[1]

        est_error = abs(elasticity - true_elasticity) if true_elasticity else None

        return ElasticityResult(
            product_id=product_id, method="OLS Log-Log",
            own_elasticity=round(elasticity, 4), std_error=round(se, 4),
            t_statistic=round(t_stat, 2), p_value=round(p_val, 4),
            ci_lower=round(ci[0], 4), ci_upper=round(ci[1], 4),
            r_squared=round(model.rsquared, 4), n_observations=len(prod_data),
            true_elasticity=true_elasticity,
            estimation_error=round(est_error, 4) if est_error else None,
        )


class PanelFEEstimator:
    """
    Panel fixed effects estimator with store and time dummies.
    Controls for unobserved store heterogeneity and common time shocks.
    """

    def estimate(
        self, df: pd.DataFrame, product_id: str,
        true_elasticity: Optional[float] = None,
    ) -> ElasticityResult:
        prod_data = df[df["product_id"] == product_id].copy()

        y = prod_data["log_quantity"].values

        # Store dummies (leave one out)
        store_dummies = pd.get_dummies(prod_data["store_id"], drop_first=True, prefix="store")
        # Quarter dummies for seasonality
        quarter_dummies = pd.get_dummies(prod_data["quarter"], drop_first=True, prefix="Q")

        X_df = pd.DataFrame({"log_price": prod_data["log_price"].values})
        if "is_promotion" in prod_data.columns:
            X_df["is_promotion"] = prod_data["is_promotion"].astype(int).values

        X_df = pd.concat([X_df, store_dummies.reset_index(drop=True),
                          quarter_dummies.reset_index(drop=True)], axis=1)
        X = sm.add_constant(X_df.values)

        # Cluster SEs by store
        store_groups = prod_data["store_id"].values
        model = OLS(y, X).fit(
            cov_type="cluster",
            cov_kwds={"groups": store_groups},
        )

        elasticity = model.params[1]
        se = model.bse[1]
        t_stat = model.tvalues[1]
        p_val = model.pvalues[1]
        ci = model.conf_int()[1]
        est_error = abs(elasticity - true_elasticity) if true_elasticity else None

        return ElasticityResult(
            product_id=product_id, method="Panel FE (Clustered SE)",
            own_elasticity=round(elasticity, 4), std_error=round(se, 4),
            t_statistic=round(t_stat, 2), p_value=round(p_val, 4),
            ci_lower=round(ci[0], 4), ci_upper=round(ci[1], 4),
            r_squared=round(model.rsquared, 4), n_observations=len(prod_data),
            true_elasticity=true_elasticity,
            estimation_error=round(est_error, 4) if est_error else None,
        )


class IVEstimator:
    """
    Instrumental Variables / 2SLS estimator.
    Uses supply-side cost shocks as instrument for price (exogenous variation).

    First stage: ln(P) = π₀ + π₁ * cost_shock + π₂ * controls + v
    Second stage: ln(Q) = α + ε * ln(P̂) + β * controls + u
    """

    def estimate(
        self, df: pd.DataFrame, product_id: str,
        instrument: str = "cost_shock",
        true_elasticity: Optional[float] = None,
    ) -> Tuple[ElasticityResult, IVDiagnostics]:
        prod_data = df[df["product_id"] == product_id].copy()

        y = prod_data["log_quantity"].values
        endog = prod_data["log_price"].values  # Endogenous regressor
        instrument_vals = prod_data[instrument].values

        # Controls
        quarter_dummies = pd.get_dummies(prod_data["quarter"], drop_first=True, prefix="Q")
        controls = sm.add_constant(quarter_dummies.values)

        # --- First stage: regress log_price on instrument + controls ---
        Z = np.column_stack([controls, instrument_vals])
        first_stage = OLS(endog, Z).fit()
        first_stage_f = first_stage.fvalue
        price_hat = first_stage.fittedvalues

        instrument_strength = "strong" if first_stage_f > config.model.iv_first_stage_f_min else "weak"

        # --- Second stage: regress log_quantity on predicted log_price ---
        X_second = np.column_stack([np.ones(len(y)), price_hat, quarter_dummies.values])
        second_stage = OLS(y, X_second).fit()

        # --- Correct SEs (manual 2SLS SE adjustment) ---
        # Use actual endogenous in residuals, not predicted
        X_actual = np.column_stack([np.ones(len(y)), endog, quarter_dummies.values])
        residuals = y - X_actual @ second_stage.params
        n = len(y)
        k = X_actual.shape[1]
        sigma2 = np.sum(residuals ** 2) / (n - k)
        XtX_inv = np.linalg.inv(X_second.T @ X_second)
        corrected_se = np.sqrt(np.diag(sigma2 * XtX_inv))

        elasticity = second_stage.params[1]
        se = corrected_se[1]
        t_stat = elasticity / se
        from scipy.stats import t as t_dist
        p_val = 2 * (1 - t_dist.cdf(abs(t_stat), n - k))

        ci_lower = elasticity - 1.96 * se
        ci_upper = elasticity + 1.96 * se

        # --- Durbin-Wu-Hausman test for endogeneity ---
        ols_result = OLS(y, X_actual).fit()
        hausman_stat = (elasticity - ols_result.params[1]) ** 2 / max(se ** 2 - ols_result.bse[1] ** 2, 1e-10)
        from scipy.stats import chi2
        hausman_p = 1 - chi2.cdf(abs(hausman_stat), 1)

        est_error = abs(elasticity - true_elasticity) if true_elasticity else None

        result = ElasticityResult(
            product_id=product_id, method="IV/2SLS",
            own_elasticity=round(elasticity, 4), std_error=round(se, 4),
            t_statistic=round(t_stat, 2), p_value=round(p_val, 6),
            ci_lower=round(ci_lower, 4), ci_upper=round(ci_upper, 4),
            r_squared=round(second_stage.rsquared, 4), n_observations=n,
            true_elasticity=true_elasticity,
            estimation_error=round(est_error, 4) if est_error else None,
        )

        diagnostics = IVDiagnostics(
            first_stage_f=round(first_stage_f, 2),
            instrument_relevance=instrument_strength,
            durbin_wu_hausman_p=round(hausman_p, 4),
            endogeneity="detected" if hausman_p < 0.05 else "not_detected",
        )

        return result, diagnostics


class CrossPriceEstimator:
    """
    Estimate cross-price elasticities via multivariate log-log regression.
    For product i: ln(Q_i) = α + ε_ii * ln(P_i) + Σ ε_ij * ln(P_j) + controls + u
    """

    def estimate(
        self, df: pd.DataFrame, products: List[str],
        true_matrix: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, List[CrossElasticityResult]]:
        """Estimate full cross-price elasticity matrix."""
        n = len(products)
        estimated_matrix = np.zeros((n, n))
        results = []

        for i, target_product in enumerate(products):
            target_data = df[df["product_id"] == target_product].copy()

            # Build wide price matrix (need all product prices aligned by week/store)
            pivot_prices = df.pivot_table(
                values="log_price", index=["date", "store_id"], columns="product_id"
            ).reset_index()

            merged = target_data.merge(
                pivot_prices, on=["date", "store_id"], suffixes=("", "_other")
            )

            y = merged["log_quantity"].values

            # Build X: log prices of all products + controls
            price_cols = [f"{p}" for p in products if p in merged.columns]
            if not price_cols:
                continue

            X_df = merged[price_cols].copy()
            X_df["const"] = 1.0

            # Add quarter dummies
            for q in [2, 3, 4]:
                X_df[f"Q{q}"] = (merged["quarter"] == q).astype(int)

            X = X_df.values
            model = OLS(y, X).fit(cov_type="HC1")

            for j, prod_j in enumerate(products):
                if prod_j in price_cols:
                    col_idx = price_cols.index(prod_j)
                    elast = model.params[col_idx]
                    se = model.bse[col_idx]
                    p_val = model.pvalues[col_idx]

                    estimated_matrix[i, j] = elast

                    if i != j:
                        if elast > 0.05 and p_val < 0.10:
                            rel = "substitute"
                        elif elast < -0.05 and p_val < 0.10:
                            rel = "complement"
                        else:
                            rel = "unrelated"

                        results.append(CrossElasticityResult(
                            product_i=target_product, product_j=prod_j,
                            cross_elasticity=round(elast, 4),
                            std_error=round(se, 4), p_value=round(p_val, 4),
                            relationship=rel,
                        ))

        return estimated_matrix, results
