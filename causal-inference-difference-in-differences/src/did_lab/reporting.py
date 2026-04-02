from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

from did_lab.diagnostics import ParallelTrendsDiagnostic, PlaceboDiagnostic
from did_lab.estimators import DidEstimate, EventStudyEstimate, SyntheticControlEstimate


HTML_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>DiD Policy Evaluation Report</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 960px; margin: 32px auto; line-height: 1.5; color: #1f2937; }
    h1, h2 { color: #111827; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 24px; }
    th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }
    th { background: #f3f4f6; }
    code { background: #f3f4f6; padding: 2px 4px; }
  </style>
</head>
<body>
  <h1>Difference-in-Differences Policy Evaluation Report</h1>
  <p>This report summarizes the baseline DiD estimate, diagnostic checks, event-study profile, and synthetic-control fallback.</p>
  <h2>Baseline estimate</h2>
  <table>
    <tr><th>Estimate</th><th>Std. Error</th><th>p-value</th><th>95% CI</th><th>N</th></tr>
    <tr>
      <td>{{ did.estimate }}</td>
      <td>{{ did.std_error }}</td>
      <td>{{ did.p_value }}</td>
      <td>[{{ did.ci_low }}, {{ did.ci_high }}]</td>
      <td>{{ did.n_obs }}</td>
    </tr>
  </table>

  <h2>Diagnostics</h2>
  <table>
    <tr><th>Check</th><th>Metric</th><th>p-value</th><th>Interpretation</th></tr>
    <tr>
      <td>Parallel trends</td>
      <td>{{ parallel.slope_diff }}</td>
      <td>{{ parallel.p_value }}</td>
      <td>{{ "Passed" if parallel.passed else "Flagged" }}</td>
    </tr>
    <tr>
      <td>Placebo treatment</td>
      <td>{{ placebo.placebo_effect }}</td>
      <td>{{ placebo.p_value }}</td>
      <td>{{ placebo_interpretation }}</td>
    </tr>
    <tr>
      <td>Event-study pretrend joint test</td>
      <td colspan="3">{{ event_joint }}</td>
    </tr>
  </table>

  <h2>Synthetic control fallback</h2>
  <table>
    <tr><th>Treated unit</th><th>Average post-treatment gap</th><th>Pre-period RMSE</th></tr>
    <tr><td>{{ synth.treated_unit }}</td><td>{{ synth.avg_gap_post }}</td><td>{{ synth.pre_rmse }}</td></tr>
  </table>

  <p>Plots are saved alongside this report in the <code>artifacts/plots</code> directory.</p>
</body>
</html>
"""
)


def _ensure_plot_dir(output_dir: Path) -> Path:
    plot_dir = output_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


def plot_group_trends(frame: pd.DataFrame, output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    plot_dir = _ensure_plot_dir(out_dir)
    agg = (
        frame.assign(group=frame["ever_treated"].map({1: "Treated", 0: "Control"}))
        .groupby(["time_id", "group"], as_index=False)["outcome"]
        .mean()
    )
    plt.figure(figsize=(8, 4.5))
    for group, grp in agg.groupby("group"):
        plt.plot(grp["time_id"], grp["outcome"], marker="o", label=group)
    treatment_start = int(frame.loc[frame["ever_treated"] == 1, "treatment_cohort"].replace(-1, pd.NA).dropna().min())
    plt.axvline(treatment_start, linestyle="--")
    plt.title("Average outcome by treatment group")
    plt.xlabel("Time period")
    plt.ylabel("Outcome")
    plt.legend()
    out = plot_dir / "group_trends.png"
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_event_study(event: EventStudyEstimate, output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    plot_dir = _ensure_plot_dir(out_dir)
    data = event.estimates
    plt.figure(figsize=(8, 4.5))
    plt.errorbar(data["event_time"], data["estimate"], yerr=1.96 * data["std_error"], fmt="o")
    plt.axhline(0.0, linestyle="--")
    plt.axvline(-1, linestyle=":")
    plt.title("Event-study coefficients")
    plt.xlabel("Periods relative to treatment")
    plt.ylabel("Effect estimate")
    out = plot_dir / "event_study.png"
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_synthetic_control(synth: SyntheticControlEstimate, output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    plot_dir = _ensure_plot_dir(out_dir)
    data = synth.trajectory
    plt.figure(figsize=(8, 4.5))
    plt.plot(data.iloc[:, 0], data["treated_actual"], label="Treated unit")
    plt.plot(data.iloc[:, 0], data["synthetic_control"], label="Synthetic control")
    plt.title(f"Synthetic control trajectory for {synth.treated_unit}")
    plt.xlabel("Time period")
    plt.ylabel("Outcome")
    plt.legend()
    out = plot_dir / "synthetic_control.png"
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def write_markdown_report(
    did: DidEstimate,
    parallel: ParallelTrendsDiagnostic,
    placebo: PlaceboDiagnostic,
    event: EventStudyEstimate,
    synth: SyntheticControlEstimate,
    output_dir: str | Path,
) -> Path:
    out_dir = Path(output_dir)
    report_dir = out_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    content = dedent(
        f"""
        # Difference-in-Differences Policy Evaluation

        ## Baseline estimate
        - Estimate: {did.estimate:.4f}
        - Std. error: {did.std_error:.4f}
        - p-value: {did.p_value:.4f}
        - 95% CI: [{did.ci_low:.4f}, {did.ci_high:.4f}]
        - Observations: {did.n_obs}

        ## Diagnostics
        - Parallel trends slope difference: {parallel.slope_diff:.4f} (p={parallel.p_value:.4f})
        - Placebo effect: {placebo.placebo_effect:.4f} (p={placebo.p_value:.4f})
        - Event-study pretrend joint p-value: {event.joint_pretrend_p_value if event.joint_pretrend_p_value is not None else 'n/a'}

        ## Synthetic control fallback
        - Treated unit: {synth.treated_unit}
        - Average post-treatment gap: {synth.avg_gap_post:.4f}
        - Pre-period RMSE: {synth.pre_rmse:.4f}

        ## Top donor weights
        {synth.donor_weights.head(5).to_markdown()}
        """
    ).strip() + "\n"
    out_path = report_dir / "policy_report.md"
    out_path.write_text(content)
    return out_path


def write_html_report(
    did: DidEstimate,
    parallel: ParallelTrendsDiagnostic,
    placebo: PlaceboDiagnostic,
    event: EventStudyEstimate,
    synth: SyntheticControlEstimate,
    output_dir: str | Path,
) -> Path:
    out_dir = Path(output_dir)
    report_dir = out_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = HTML_TEMPLATE.render(
        did=did,
        parallel=parallel,
        placebo=placebo,
        placebo_interpretation="Should be close to zero in pre-period" if placebo.p_value >= 0.05 else "Potential early signal or violation",
        event_joint=(
            f"p={event.joint_pretrend_p_value:.4f}" if event.joint_pretrend_p_value is not None else "Not available"
        ),
        synth=synth,
    )
    out_path = report_dir / "policy_report.html"
    out_path.write_text(payload)
    return out_path
