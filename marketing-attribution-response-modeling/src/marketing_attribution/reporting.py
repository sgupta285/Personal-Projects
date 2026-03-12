from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_plot(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_reports(
    baselines: pd.DataFrame,
    model_attr: pd.DataFrame,
    curves: pd.DataFrame,
    budget_df: pd.DataFrame,
    journeys: pd.DataFrame,
    touchpoints: pd.DataFrame,
    reports_dir: Path,
    dashboard_dir: Path,
    docs_dir: Path,
) -> dict:
    reports_dir.mkdir(parents=True, exist_ok=True)
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    baseline_pivot = baselines.pivot(index="channel", columns="method", values="conversions").fillna(0).sort_index()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    baseline_pivot.plot(kind="bar", ax=ax)
    ax.set_title("Attributed conversions by reporting method")
    ax.set_ylabel("Conversions")
    ax.set_xlabel("Channel")
    _save_plot(fig, reports_dir / "attribution_comparison.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(model_attr["channel"], model_attr["attributed_conversions"])
    ax.set_title("Model-based attributed conversions")
    ax.set_ylabel("Attributed conversions")
    ax.tick_params(axis="x", rotation=30)
    _save_plot(fig, reports_dir / "model_attribution.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.scatter(curves["recent_avg_spend"], curves["marginal_conversions_per_dollar"], s=90)
    for _, row in curves.iterrows():
        ax.annotate(row["channel"], (row["recent_avg_spend"], row["marginal_conversions_per_dollar"]))
    ax.set_title("Current spend vs marginal conversion return")
    ax.set_xlabel("Recent average daily spend")
    ax.set_ylabel("Marginal conversions per dollar")
    _save_plot(fig, reports_dir / "response_curves.png")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    budget_plot = budget_df.set_index("channel")[["current_spend", "recommended_spend"]]
    budget_plot.plot(kind="bar", ax=ax)
    ax.set_title("Current vs recommended spend")
    ax.set_ylabel("Daily spend")
    ax.tick_params(axis="x", rotation=30)
    _save_plot(fig, reports_dir / "budget_reallocation.png")

    total_conversions = int(journeys["converted"].sum())
    total_revenue = float(journeys["revenue"].sum())
    total_spend = float(touchpoints["spend"].sum())
    conv_rate = total_conversions / max(len(journeys), 1)
    summary = {
        "journeys": int(len(journeys)),
        "touchpoints": int(len(touchpoints)),
        "conversion_rate": round(conv_rate, 4),
        "total_conversions": total_conversions,
        "total_revenue": round(total_revenue, 2),
        "total_media_spend": round(total_spend, 2),
        "blended_roas": round(total_revenue / total_spend, 3) if total_spend > 0 else 0.0,
        "best_marginal_return_channel": str(curves.sort_values("marginal_conversions_per_dollar", ascending=False).iloc[0]["channel"]),
        "lowest_marginal_return_channel": str(curves.sort_values("marginal_conversions_per_dollar", ascending=True).iloc[0]["channel"]),
        "recommended_conversion_lift_per_day": round(float(budget_df["conversion_delta"].sum()), 2),
        "recommended_revenue_lift_per_day": round(float(budget_df["revenue_delta"].sum()), 2),
    }
    (reports_dir / "summary_metrics.json").write_text(json.dumps(summary, indent=2))

    top_shift_to = budget_df.sort_values("spend_delta", ascending=False).head(2)
    top_shift_from = budget_df.sort_values("spend_delta", ascending=True).head(2)
    to_table = top_shift_to[["channel", "spend_delta"]].round(2).to_markdown(index=False)
    from_table = top_shift_from[["channel", "spend_delta"]].round(2).to_markdown(index=False)

    stakeholder = f"""# Stakeholder Summary

## Executive summary

This measurement pack compares rule-based attribution, a model-based attribution view, and spend response curves for the same synthetic marketing system. The outputs are designed for budget planning, not for making causal claims stronger than the data supports.

## Headline numbers

- Journeys analyzed: **{summary['journeys']:,}**
- Touchpoints analyzed: **{summary['touchpoints']:,}**
- Conversion rate: **{summary['conversion_rate']:.2%}**
- Total conversions: **{summary['total_conversions']:,}**
- Revenue: **${summary['total_revenue']:,.2f}**
- Media spend: **${summary['total_media_spend']:,.2f}**
- Blended ROAS: **{summary['blended_roas']:.2f}**

## Attribution readout

- Rule-based methods disagree most on direct, email, and paid social.
- The model-based view keeps search and email strong while reducing some of the last-touch inflation that shows up in direct traffic.
- The biggest difference between the baseline and model-based views is that upper- and mid-funnel channels recover more contribution once the full path is considered.

## Response curve readout

- Best current marginal return: **{summary['best_marginal_return_channel']}**
- Lowest current marginal return: **{summary['lowest_marginal_return_channel']}**
- Estimated daily conversion lift from reallocation: **{summary['recommended_conversion_lift_per_day']:.2f}**
- Estimated daily revenue lift from reallocation: **${summary['recommended_revenue_lift_per_day']:,.2f}**

## Budget recommendation

Move budget toward:
{to_table}

Move budget away from:
{from_table}

## Measurement caveats

- Do not interpret this as causal incrementality proof.
- Keep holdout or geo experiments as the next validation layer for any major budget move.
- Direct and organic channels still need careful handling because they often absorb intent created elsewhere.

## Experiment hooks

Before scaling the reallocation plan, validate one or more of the following:

1. geo-based holdout for search or social
2. incrementality test for email cadence
3. regional affiliate on/off test
4. creative holdout inside paid social
"""
    (docs_dir / "STAKEHOLDER_SUMMARY.md").write_text(stakeholder)

    dashboard_html = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>Marketing Attribution Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
    h1, h2 {{ margin-bottom: 0.3rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 14px; margin: 18px 0 26px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 14px; background: #fafafa; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 24px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f3f3f3; }}
    img {{ max-width: 100%; margin: 18px 0 28px; border: 1px solid #e2e2e2; }}
  </style>
</head>
<body>
  <h1>Marketing Attribution & Response Modeling</h1>
  <p>Local dashboard snapshot generated from the bootstrap pipeline.</p>
  <div class=\"grid\">
    <div class=\"card\"><strong>Journeys</strong><br>{summary['journeys']:,}</div>
    <div class=\"card\"><strong>Conversions</strong><br>{summary['total_conversions']:,}</div>
    <div class=\"card\"><strong>Conversion rate</strong><br>{summary['conversion_rate']:.2%}</div>
    <div class=\"card\"><strong>Blended ROAS</strong><br>{summary['blended_roas']:.2f}</div>
  </div>
  <h2>Rule-based attribution</h2>
  {baselines.round(2).to_html(index=False)}
  <img src=\"../reports/attribution_comparison.png\" alt=\"Attribution comparison\">
  <h2>Model-based attribution</h2>
  {model_attr.round(2).to_html(index=False)}
  <img src=\"../reports/model_attribution.png\" alt=\"Model attribution\">
  <h2>Response curves and reallocation</h2>
  {curves.round(4).to_html(index=False)}
  <img src=\"../reports/response_curves.png\" alt=\"Response curves\">
  {budget_df[['channel', 'current_spend', 'recommended_spend', 'spend_delta', 'conversion_delta', 'revenue_delta']].round(2).to_html(index=False)}
  <img src=\"../reports/budget_reallocation.png\" alt=\"Budget reallocation\">
</body>
</html>"""
    (dashboard_dir / "index.html").write_text(dashboard_html)
    return summary
