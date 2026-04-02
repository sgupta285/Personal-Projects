from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from jinja2 import Template

from mlprep.validation import ValidationFinding, findings_to_summary


HTML_TEMPLATE = Template(
    """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>ML Data Preparation Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }
      h1, h2 { margin-bottom: 8px; }
      .card { border: 1px solid #d1d5db; border-radius: 10px; padding: 16px; margin-bottom: 18px; }
      table { border-collapse: collapse; width: 100%; font-size: 14px; }
      th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }
      th { background: #f3f4f6; }
      .passed { color: #166534; }
      .warning { color: #92400e; }
      .failed { color: #991b1b; }
      code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>ML Data Preparation Report</h1>
    <p>Dataset rows: <strong>{{ dataset_rows }}</strong> | columns: <strong>{{ dataset_columns }}</strong></p>

    <div class="card">
      <h2>Validation summary</h2>
      <ul>
        <li>Passed: {{ summary.passed }}</li>
        <li>Warnings: {{ summary.warning }}</li>
        <li>Failed: {{ summary.failed }}</li>
      </ul>
      <table>
        <thead><tr><th>Check</th><th>Status</th><th>Details</th></tr></thead>
        <tbody>
        {% for finding in findings %}
          <tr>
            <td>{{ finding.check }}</td>
            <td class="{{ finding.status }}">{{ finding.status }}</td>
            <td>{{ finding.details }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Completeness dashboard</h2>
      {{ missingness_table }}
    </div>

    <div class="card">
      <h2>Distribution shift snapshot</h2>
      {{ shift_table }}
    </div>

    <div class="card">
      <h2>Top correlations</h2>
      {{ correlation_table }}
    </div>
  </body>
</html>
"""
)


def build_report(
    original_df: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    findings: list[ValidationFinding],
    html_path: str,
    json_path: str,
) -> dict:
    summary = findings_to_summary(findings)
    missingness = original_df.isna().mean().sort_values(ascending=False).to_frame("null_rate")

    numeric_columns = train_df.select_dtypes(include="number").columns
    shift_rows = []
    for column in numeric_columns:
        shift_rows.append({
            "column": column,
            "train_mean": round(float(train_df[column].mean()), 4),
            "test_mean": round(float(test_df[column].mean()), 4),
            "delta": round(float(test_df[column].mean() - train_df[column].mean()), 4),
        })
    shift_df = pd.DataFrame(shift_rows).sort_values("delta", key=lambda s: s.abs(), ascending=False)

    correlations = (
        original_df.select_dtypes(include="number").corr().stack().reset_index(name="correlation")
    )
    correlations = correlations[correlations["level_0"] < correlations["level_1"]]
    correlations = correlations.reindex(correlations["correlation"].abs().sort_values(ascending=False).index).head(10)

    payload = {
        "dataset_rows": int(len(original_df)),
        "dataset_columns": int(len(original_df.columns)),
        "validation_summary": summary,
        "top_missing_columns": missingness.head(10).reset_index().rename(columns={"index": "column"}).to_dict(orient="records"),
        "distribution_shift": shift_df.head(10).to_dict(orient="records"),
        "top_correlations": correlations.to_dict(orient="records"),
    }

    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    html = HTML_TEMPLATE.render(
        dataset_rows=payload["dataset_rows"],
        dataset_columns=payload["dataset_columns"],
        summary=type("Summary", (), summary),
        findings=findings,
        missingness_table=missingness.head(12).to_html(classes="table", border=0),
        shift_table=shift_df.head(12).to_html(index=False, border=0),
        correlation_table=correlations.to_html(index=False, border=0),
    )
    Path(html_path).write_text(html, encoding="utf-8")
    return payload
