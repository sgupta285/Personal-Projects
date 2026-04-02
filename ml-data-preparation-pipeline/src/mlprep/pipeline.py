from __future__ import annotations

from pathlib import Path

import pandas as pd

from mlprep.data_loader import load_dataset
from mlprep.feature_engineering import FeatureEngineer
from mlprep.preprocessing import Preprocessor
from mlprep.reporting import build_report
from mlprep.validation import DataValidator


class PreparationPipeline:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.validator = DataValidator(config)
        self.engineer = FeatureEngineer(config)
        self.preprocessor = Preprocessor(config)

    def run(self) -> dict:
        raw_df = load_dataset(self.config["dataset"]["path"])
        self.logger.info("Loaded %s rows and %s columns", len(raw_df), len(raw_df.columns))

        findings = self.validator.run(raw_df)
        engineered_df = self.engineer.transform(raw_df)
        prepared = self.preprocessor.prepare(engineered_df, self.config["dataset"]["target_column"])

        artifacts_cfg = self.config["artifacts"]
        Path(artifacts_cfg["transformed_train_path"]).parent.mkdir(parents=True, exist_ok=True)
        prepared.X_train_transformed.assign(target=prepared.y_train).to_csv(
            artifacts_cfg["transformed_train_path"], index=False
        )
        prepared.X_test_transformed.assign(target=prepared.y_test).to_csv(
            artifacts_cfg["transformed_test_path"], index=False
        )
        self.preprocessor.persist_pipeline(prepared.pipeline, artifacts_cfg["fitted_pipeline_path"])

        report_cfg = self.config["reporting"]
        summary = build_report(
            original_df=engineered_df,
            train_df=prepared.X_train_raw,
            test_df=prepared.X_test_raw,
            findings=findings,
            html_path=report_cfg["html_report_path"],
            json_path=report_cfg["json_summary_path"],
        )
        self.logger.info("Pipeline finished. Report written to %s", report_cfg["html_report_path"])
        return {
            "findings": findings,
            "prepared": prepared,
            "summary": summary,
        }
