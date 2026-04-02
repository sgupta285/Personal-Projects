from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(slots=True)
class PreparedData:
    X_train_raw: pd.DataFrame
    X_test_raw: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    X_train_transformed: pd.DataFrame
    X_test_transformed: pd.DataFrame
    pipeline: Pipeline


class Preprocessor:
    def __init__(self, config: dict):
        self.config = config

    def prepare(self, df: pd.DataFrame, target_column: str) -> PreparedData:
        dataset_cfg = self.config["dataset"]
        prep_cfg = self.config["preprocessing"]
        feature_df = df.drop(columns=[target_column])
        target = df[target_column]

        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            feature_df,
            target,
            train_size=dataset_cfg["train_size"],
            random_state=dataset_cfg["random_state"],
            stratify=target,
        )

        X_train_raw = self._winsorize(X_train_raw, prep_cfg["numeric_columns"])
        X_test_raw = self._apply_winsor_bounds(X_train_raw, X_test_raw, prep_cfg["numeric_columns"])

        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )
        boolean_transformer = Pipeline(
            steps=[("imputer", SimpleImputer(strategy="most_frequent"))]
        )

        transformer = ColumnTransformer(
            transformers=[
                ("numeric", numeric_transformer, prep_cfg["numeric_columns"]),
                ("categorical", categorical_transformer, prep_cfg["categorical_columns"]),
                ("boolean", boolean_transformer, prep_cfg["boolean_columns"]),
            ],
            remainder="drop",
        )

        pipeline = Pipeline(steps=[("transformer", transformer)])
        X_train_array = pipeline.fit_transform(X_train_raw)
        X_test_array = pipeline.transform(X_test_raw)

        feature_names = pipeline.named_steps["transformer"].get_feature_names_out()
        X_train_transformed = pd.DataFrame(X_train_array, columns=feature_names, index=X_train_raw.index)
        X_test_transformed = pd.DataFrame(X_test_array, columns=feature_names, index=X_test_raw.index)

        return PreparedData(
            X_train_raw=X_train_raw,
            X_test_raw=X_test_raw,
            y_train=y_train,
            y_test=y_test,
            X_train_transformed=X_train_transformed,
            X_test_transformed=X_test_transformed,
            pipeline=pipeline,
        )

    def persist_pipeline(self, pipeline: Pipeline, path: str) -> None:
        dump(pipeline, path)

    def _winsorize(self, df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
        lower_q, upper_q = self.config["preprocessing"]["winsorize_limits"]
        adjusted = df.copy()
        for column in numeric_columns:
            lower = adjusted[column].quantile(lower_q)
            upper = adjusted[column].quantile(upper_q)
            adjusted[column] = adjusted[column].clip(lower=lower, upper=upper)
        return adjusted

    def _apply_winsor_bounds(self, train_df: pd.DataFrame, test_df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
        lower_q, upper_q = self.config["preprocessing"]["winsorize_limits"]
        adjusted = test_df.copy()
        for column in numeric_columns:
            lower = train_df[column].quantile(lower_q)
            upper = train_df[column].quantile(upper_q)
            adjusted[column] = adjusted[column].clip(lower=lower, upper=upper)
        return adjusted
