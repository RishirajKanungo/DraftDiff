from __future__ import annotations

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


TARGET = "blue_win"
NON_FEATURE_COLS = {TARGET, "match_id", "patch"}


def get_feature_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if c not in NON_FEATURE_COLS]


def train_model(input_parquet: Path, output_model: Path) -> dict:
    df = pd.read_parquet(input_parquet)
    X = df[get_feature_columns(df)]
    y = df[TARGET].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler(with_mean=False)),
            (
                "clf",
                LGBMClassifier(
                    n_estimators=600,
                    learning_rate=0.03,
                    max_depth=-1,
                    num_leaves=64,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.0,
                    reg_lambda=1.0,
                    random_state=42,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    val_proba = pipeline.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, val_proba)
    brier = brier_score_loss(y_val, val_proba)

    output_model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "feature_names": get_feature_columns(df)}, output_model)

    return {"val_auc": float(auc), "val_brier": float(brier), "n_train": int(len(X_train)), "n_val": int(len(X_val))}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Path to training parquet")
    parser.add_argument("--output", type=Path, required=True, help="Path to write model.joblib")
    args = parser.parse_args()

    metrics = train_model(args.input, args.output)
    print(metrics)


