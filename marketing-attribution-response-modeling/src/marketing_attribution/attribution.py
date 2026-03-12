from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def compute_rule_based_attribution(touchpoints: pd.DataFrame, journeys: pd.DataFrame) -> pd.DataFrame:
    converted = journeys[journeys["converted"] == 1][["journey_id", "revenue"]].copy()
    touches = touchpoints.merge(converted, on="journey_id", how="inner")
    touches = touches.sort_values(["journey_id", "path_position", "event_time"]).copy()

    first = touches.drop_duplicates("journey_id", keep="first").groupby("channel", as_index=False).agg(
        conversions=("journey_id", "count"),
        attributed_revenue=("revenue", "sum"),
    )
    first["method"] = "first_touch"

    last = touches.drop_duplicates("journey_id", keep="last").groupby("channel", as_index=False).agg(
        conversions=("journey_id", "count"),
        attributed_revenue=("revenue", "sum"),
    )
    last["method"] = "last_touch"

    linear = touches.copy()
    lengths = linear.groupby("journey_id").size().rename("path_length")
    linear = linear.merge(lengths, on="journey_id", how="left")
    linear["conversions"] = 1.0 / linear["path_length"]
    linear["attributed_revenue"] = linear["revenue"] / linear["path_length"]
    linear = linear.groupby("channel", as_index=False).agg(
        conversions=("conversions", "sum"),
        attributed_revenue=("attributed_revenue", "sum"),
    )
    linear["method"] = "linear"

    spend = touchpoints.groupby("channel", as_index=False)["spend"].sum()
    combined = pd.concat([first, last, linear], ignore_index=True)
    combined = combined.merge(spend, on="channel", how="left")
    combined["spend"] = combined["spend"].fillna(0.0)
    combined["cac"] = np.where(combined["conversions"] > 0, combined["spend"] / combined["conversions"], 0.0)
    combined["roas"] = np.where(combined["spend"] > 0, combined["attributed_revenue"] / combined["spend"], 0.0)
    return combined.sort_values(["method", "conversions"], ascending=[True, False]).reset_index(drop=True)


def build_user_feature_matrix(touchpoints: pd.DataFrame, journeys: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    touch_counts = touchpoints.pivot_table(index="journey_id", columns="channel", values="path_position", aggfunc="count", fill_value=0)
    touch_counts.columns = [f"touches__{c}" for c in touch_counts.columns]

    click_counts = touchpoints.pivot_table(index="journey_id", columns="channel", values="clicks", aggfunc="sum", fill_value=0)
    click_counts.columns = [f"clicks__{c}" for c in click_counts.columns]

    spend_counts = touchpoints.pivot_table(index="journey_id", columns="channel", values="spend", aggfunc="sum", fill_value=0)
    spend_counts.columns = [f"spend__{c}" for c in spend_counts.columns]

    meta = journeys.set_index("journey_id")[["segment", "device", "region", "product_category", "path_length", "total_spend", "revenue", "converted"]]
    X = pd.concat([touch_counts, click_counts, spend_counts, meta.drop(columns=["revenue", "converted"])], axis=1).fillna(0)
    X = pd.get_dummies(X, columns=["segment", "device", "region", "product_category"], drop_first=False)
    y = meta["converted"].astype(int)
    aux = meta[["revenue", "converted"]].copy()
    return X, y, aux


def compute_model_based_attribution(touchpoints: pd.DataFrame, journeys: pd.DataFrame) -> tuple[pd.DataFrame, LogisticRegression]:
    X, y, aux = build_user_feature_matrix(touchpoints, journeys)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.astype(float))
    model = LogisticRegression(max_iter=1200, solver="lbfgs")
    model.fit(X_scaled, y)

    p_full = model.predict_proba(X_scaled)[:, 1]
    channels = sorted(touchpoints["channel"].unique().tolist())
    raw = []

    for channel in channels:
        ablated = X.copy()
        for prefix in ("touches__", "clicks__", "spend__"):
            col = f"{prefix}{channel}"
            if col in ablated.columns:
                ablated[col] = 0
        p_without = model.predict_proba(scaler.transform(ablated.astype(float)))[:, 1]
        delta = np.clip(p_full - p_without, 0.0, None)
        raw.append(
            {
                "channel": channel,
                "raw_contribution": float(delta.sum()),
                "journeys_touched": int((X.get(f"touches__{channel}", 0) > 0).sum()),
            }
        )

    result = pd.DataFrame(raw)
    total_actual_conversions = float(aux["converted"].sum())
    total_raw = float(result["raw_contribution"].sum()) or 1.0
    result["attributed_conversions"] = result["raw_contribution"] / total_raw * total_actual_conversions

    converted_ids = aux[aux["converted"] == 1].index
    touches_conv = touchpoints[touchpoints["journey_id"].isin(converted_ids)]
    conv_journeys = journeys.set_index("journey_id")
    overall_aov = float(conv_journeys[conv_journeys["converted"] == 1]["revenue"].mean())
    avg_revenue_by_channel = {}
    for channel in channels:
        journey_ids = touches_conv.loc[touches_conv["channel"] == channel, "journey_id"].unique().tolist()
        if journey_ids:
            avg_revenue_by_channel[channel] = float(conv_journeys.loc[journey_ids, "revenue"].replace(0, np.nan).dropna().mean())
        else:
            avg_revenue_by_channel[channel] = overall_aov

    result["attributed_revenue"] = result.apply(lambda row: row["attributed_conversions"] * avg_revenue_by_channel[row["channel"]], axis=1)
    spend = touchpoints.groupby("channel", as_index=False)["spend"].sum()
    result = result.merge(spend, on="channel", how="left")
    result["spend"] = result["spend"].fillna(0.0)
    result["cac"] = np.where(result["attributed_conversions"] > 0, result["spend"] / result["attributed_conversions"], 0.0)
    result["roas"] = np.where(result["spend"] > 0, result["attributed_revenue"] / result["spend"], 0.0)
    result = result.sort_values("attributed_conversions", ascending=False).reset_index(drop=True)
    return result, model
