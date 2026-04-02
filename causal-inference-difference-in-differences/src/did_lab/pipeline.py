from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from did_lab.config import AnalysisConfig, BenchmarkConfig, DataConfig
from did_lab.data import generate_sample_panel, load_panel, panel_summary, save_panel
from did_lab.diagnostics import parallel_trends_test, placebo_test
from did_lab.estimators import event_study, synthetic_control, twfe_did
from did_lab.reporting import (
    plot_event_study,
    plot_group_trends,
    plot_synthetic_control,
    write_html_report,
    write_markdown_report,
)


def build_sample_dataset(config: DataConfig) -> Path:
    frame = generate_sample_panel(config)
    return save_panel(frame, config.output_path)


def run_analysis(data_path: str | Path, config: AnalysisConfig) -> dict:
    frame = load_panel(data_path)
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    did = twfe_did(frame, config.outcome_col, config.unit_col, config.time_col, config.cluster_col)
    parallel = parallel_trends_test(
        frame,
        config.outcome_col,
        config.unit_col,
        config.time_col,
        config.pre_periods_for_parallel_trends,
    )
    placebo = placebo_test(
        frame,
        config.outcome_col,
        config.unit_col,
        config.time_col,
        config.cluster_col,
        config.placebo_shift,
    )
    event = event_study(frame, config.outcome_col, config.unit_col, config.time_col, config.cluster_col)
    treatment_start = int(frame.loc[frame[config.ever_treated_col] == 1, config.cohort_col].replace(-1, None).dropna().min())
    synth = synthetic_control(frame, config.outcome_col, config.unit_col, config.time_col, treatment_start)

    plot_group_trends(frame, out_dir)
    plot_event_study(event, out_dir)
    plot_synthetic_control(synth, out_dir)
    write_markdown_report(did, parallel, placebo, event, synth, out_dir)
    write_html_report(did, parallel, placebo, event, synth, out_dir)

    summary = {
        "dataset": panel_summary(frame),
        "did": asdict(did),
        "parallel_trends": asdict(parallel),
        "placebo": asdict(placebo),
        "event_study": {
            "joint_pretrend_p_value": event.joint_pretrend_p_value,
            "rows": event.estimates.to_dict(orient="records"),
        },
        "synthetic_control": {
            "treated_unit": synth.treated_unit,
            "avg_gap_post": synth.avg_gap_post,
            "pre_rmse": synth.pre_rmse,
            "top_weights": synth.donor_weights.head(5).round(6).to_dict(),
        },
    }
    (out_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def run_benchmark(config: BenchmarkConfig, data_config: DataConfig, analysis_config: AnalysisConfig) -> dict:
    out_path = Path(config.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for rep in range(config.replications):
        trial_config = DataConfig(**{**asdict(data_config), "seed": config.seed + rep})
        frame = generate_sample_panel(trial_config)
        did = twfe_did(frame, analysis_config.outcome_col, analysis_config.unit_col, analysis_config.time_col, analysis_config.cluster_col)
        parallel = parallel_trends_test(
            frame,
            analysis_config.outcome_col,
            analysis_config.unit_col,
            analysis_config.time_col,
            analysis_config.pre_periods_for_parallel_trends,
        )
        results.append(
            {
                "replication": rep,
                "did_estimate": did.estimate,
                "did_p_value": did.p_value,
                "parallel_trends_p_value": parallel.p_value,
                "parallel_trends_passed": parallel.passed,
            }
        )
    aggregate = {
        "replications": config.replications,
        "mean_estimate": sum(r["did_estimate"] for r in results) / len(results),
        "share_significant": sum(r["did_p_value"] < 0.05 for r in results) / len(results),
        "share_parallel_trends_passed": sum(r["parallel_trends_passed"] for r in results) / len(results),
        "runs": results,
    }
    out_path.write_text(json.dumps(aggregate, indent=2))
    return aggregate
