"""
Train fraud detection model on synthetic transaction data.
Handles class imbalance with SMOTE + ensemble methods (XGBoost).
Outputs a serialized model + metadata for serving.
"""

import os
import json
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib


SEED = 42
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def generate_synthetic_data(n_samples: int = 284_000) -> pd.DataFrame:
    """
    Generate synthetic transaction data mimicking credit card fraud patterns.
    ~0.17% fraud rate (realistic class imbalance).
    """
    np.random.seed(SEED)

    n_fraud = int(n_samples * 0.0017)
    n_legit = n_samples - n_fraud

    # 28 PCA-like features (V1-V28) + Amount + Time
    legit_features = np.random.randn(n_legit, 28) * 1.0
    fraud_features = np.random.randn(n_fraud, 28) * 1.5 + np.random.choice([-1, 1], size=(n_fraud, 28)) * 0.8

    legit_amount = np.abs(np.random.lognormal(mean=4.0, sigma=1.5, size=n_legit))
    fraud_amount = np.abs(np.random.lognormal(mean=5.0, sigma=2.0, size=n_fraud))

    legit_time = np.sort(np.random.uniform(0, 172800, size=n_legit))
    fraud_time = np.random.uniform(0, 172800, size=n_fraud)

    # Combine
    features = np.vstack([legit_features, fraud_features])
    amounts = np.concatenate([legit_amount, fraud_amount]).reshape(-1, 1)
    times = np.concatenate([legit_time, fraud_time]).reshape(-1, 1)
    labels = np.concatenate([np.zeros(n_legit), np.ones(n_fraud)])

    data = np.hstack([times, features, amounts])
    columns = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

    df = pd.DataFrame(data, columns=columns)
    df["Class"] = labels.astype(int)

    # Shuffle
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return df


def train_model():
    print("=" * 60)
    print("FRAUD DETECTION MODEL TRAINING")
    print("=" * 60)

    # Generate data
    print("\n[1/5] Generating synthetic transaction data...")
    df = generate_synthetic_data(284_000)
    print(f"  Total samples: {len(df):,}")
    print(f"  Fraud samples: {df['Class'].sum():,.0f} ({df['Class'].mean()*100:.2f}%)")
    print(f"  Legit samples: {(df['Class']==0).sum():,}")

    # Prepare features
    feature_cols = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]
    X = df[feature_cols].values
    y = df["Class"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    print(f"\n[2/5] Splitting data...")
    print(f"  Train: {len(X_train):,}  |  Test: {len(X_test):,}")
    print(f"  Train fraud rate: {y_train.mean()*100:.2f}%")

    # Scale
    print("\n[3/5] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # SMOTE oversampling on train set
    print("\n[4/5] Applying SMOTE + training ensemble...")
    smote = SMOTE(random_state=SEED, sampling_strategy=0.5)
    X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
    print(f"  After SMOTE: {len(X_train_res):,} samples (fraud: {y_train_res.mean()*100:.1f}%)")

    # XGBoost with tuned hyperparameters
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=1.0,  # Already balanced via SMOTE
        random_state=SEED,
        eval_metric="logloss",
        use_label_encoder=False,
        n_jobs=-1,
    )

    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=SEED,
        n_jobs=-1,
    )

    # Voting ensemble
    ensemble = VotingClassifier(
        estimators=[("xgb", xgb_model), ("rf", rf_model)],
        voting="soft",
        weights=[2, 1],  # Weight XGBoost higher
    )

    start = time.time()
    ensemble.fit(X_train_res, y_train_res)
    train_time = time.time() - start
    print(f"  Training time: {train_time:.1f}s")

    # Evaluate
    print("\n[5/5] Evaluating model...")
    y_pred = ensemble.predict(X_test_scaled)
    y_proba = ensemble.predict_proba(X_test_scaled)[:, 1]

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  AUC-ROC:   {auc:.4f}")
    print(f"\n  Confusion Matrix:")
    print(f"    TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"    FN={cm[1][0]:,}  TP={cm[1][1]:,}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Legit', 'Fraud'])}")

    # Cross-validation
    print("  Running 5-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = cross_val_score(
        xgb_model, X_train_res, y_train_res, cv=cv, scoring="f1", n_jobs=-1
    )
    print(f"  CV F1 scores: {cv_scores.round(4)}")
    print(f"  Mean CV F1:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Save model artifacts
    os.makedirs(DATA_DIR, exist_ok=True)

    model_path = os.path.join(DATA_DIR, "fraud_model.joblib")
    scaler_path = os.path.join(DATA_DIR, "scaler.joblib")
    metadata_path = os.path.join(DATA_DIR, "model_metadata.json")

    joblib.dump(ensemble, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "model_type": "VotingClassifier(XGBoost + RandomForest)",
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "training_samples": len(X_train_res),
        "test_samples": len(X_test),
        "smote_strategy": 0.5,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "auc_roc": round(auc, 4),
        "cv_f1_mean": round(cv_scores.mean(), 4),
        "cv_f1_std": round(cv_scores.std(), 4),
        "training_time_seconds": round(train_time, 1),
        "threshold": 0.5,
        "train_feature_means": scaler.mean_.tolist(),
        "train_feature_stds": scaler.scale_.tolist(),
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n  Model saved:    {model_path}")
    print(f"  Scaler saved:   {scaler_path}")
    print(f"  Metadata saved: {metadata_path}")
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    return ensemble, scaler, metadata


if __name__ == "__main__":
    train_model()
