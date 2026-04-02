from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(slots=True)
class ValidationFinding:
    check: str
    status: str
    details: str


class DataValidator:
    def __init__(self, config: dict):
        self.config = config

    def run(self, df: pd.DataFrame) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        findings.extend(self._check_required_columns(df))
        findings.extend(self._check_null_rates(df))
        findings.extend(self._check_duplicates(df))
        findings.extend(self._check_anomalies(df))
        findings.extend(self._check_expectations(df))
        return findings

    def _check_required_columns(self, df: pd.DataFrame) -> list[ValidationFinding]:
        required = self.config["validation"]["required_columns"]
        missing = [column for column in required if column not in df.columns]
        if missing:
            return [ValidationFinding("required_columns", "failed", f"Missing columns: {missing}")]
        return [ValidationFinding("required_columns", "passed", "All required columns are present")]

    def _check_null_rates(self, df: pd.DataFrame) -> list[ValidationFinding]:
        threshold = float(self.config["validation"]["null_threshold"])
        violations = []
        for column, value in df.isna().mean().to_dict().items():
            if value > threshold:
                violations.append(f"{column}={value:.2%}")
        if violations:
            return [ValidationFinding("null_threshold", "failed", "; ".join(violations))]
        return [ValidationFinding("null_threshold", "passed", f"No column exceeded {threshold:.0%} null threshold")]

    def _check_duplicates(self, df: pd.DataFrame) -> list[ValidationFinding]:
        duplicate_keys = self.config["validation"].get("duplicate_key_columns", [])
        if not duplicate_keys:
            return []
        duplicate_count = int(df.duplicated(subset=duplicate_keys).sum())
        status = "failed" if duplicate_count else "passed"
        details = f"Detected {duplicate_count} duplicate keys across {duplicate_keys}"
        return [ValidationFinding("duplicate_keys", status, details)]

    def _check_anomalies(self, df: pd.DataFrame) -> list[ValidationFinding]:
        numeric_df = df.select_dtypes(include=[np.number])
        threshold = float(self.config["validation"].get("anomaly_zscore_threshold", 3.0))
        if numeric_df.empty:
            return []
        safe_std = numeric_df.std(ddof=0).replace(0, np.nan)
        zscores = ((numeric_df - numeric_df.mean()) / safe_std).abs().fillna(0)
        anomalous_cells = int((zscores > threshold).sum().sum())
        status = "warning" if anomalous_cells else "passed"
        details = f"{anomalous_cells} anomalous numeric cells exceeded z-score threshold {threshold}"
        return [ValidationFinding("anomaly_detection", status, details)]

    def _check_expectations(self, df: pd.DataFrame) -> list[ValidationFinding]:
        expectation_path = Path("configs/expectations.json")
        if not expectation_path.exists():
            return []
        expectations = json.loads(expectation_path.read_text(encoding="utf-8"))["expectations"]
        findings: list[ValidationFinding] = []
        for expectation in expectations:
            expectation_type = expectation["type"]
            column = expectation.get("column", "")
            if expectation_type == "expect_column_to_exist":
                status = "passed" if column in df.columns else "failed"
                details = f"Column {column} {'exists' if status == 'passed' else 'is missing'}"
            elif expectation_type == "expect_column_values_to_not_be_null":
                missing_count = int(df[column].isna().sum()) if column in df.columns else len(df)
                status = "passed" if missing_count == 0 else "failed"
                details = f"Column {column} has {missing_count} null values"
            elif expectation_type == "expect_column_values_to_be_between":
                if column not in df.columns:
                    status = "failed"
                    details = f"Column {column} is missing"
                else:
                    min_value = expectation["min_value"]
                    max_value = expectation["max_value"]
                    invalid = int(((df[column] < min_value) | (df[column] > max_value)).sum())
                    status = "passed" if invalid == 0 else "failed"
                    details = f"Column {column} has {invalid} values outside [{min_value}, {max_value}]"
            elif expectation_type == "expect_column_values_to_be_in_set":
                if column not in df.columns:
                    status = "failed"
                    details = f"Column {column} is missing"
                else:
                    allowed = set(expectation["value_set"])
                    invalid = int((~df[column].isin(allowed)).sum())
                    status = "passed" if invalid == 0 else "failed"
                    details = f"Column {column} has {invalid} values outside the allowed set"
            else:
                continue
            findings.append(ValidationFinding(f"expectation::{expectation_type}", status, details))
        return findings


def findings_to_summary(findings: list[ValidationFinding]) -> dict[str, int]:
    summary = {"passed": 0, "warning": 0, "failed": 0}
    for finding in findings:
        summary[finding.status] = summary.get(finding.status, 0) + 1
    return summary
