"""Train a simple clause -> risk_level model from base_contract_clauses.csv.

This is a lightweight baseline you can use to quickly validate new CSV files.
It trains a TF-IDF + LogisticRegression classifier and saves it to data/risk_model.pkl.

Usage:
  /home/sumit/Documents/NLP Project/.venv/bin/python backend/scripts/train_risk_model.py

Optional:
  ... train_risk_model.py --data Graphs-for-NLP/data/base_contract_clauses.csv --out Graphs-for-NLP/data/risk_model.pkl
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


ALLOWED_LABELS = {"low", "medium", "high"}


def _normalize_label(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x).strip().lower()


def _load_training_df(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "clause_text" not in df.columns:
        raise SystemExit(f"Missing required column 'clause_text' in {csv_path}")
    if "risk_level" not in df.columns:
        raise SystemExit(f"Missing required column 'risk_level' in {csv_path}")

    df = df[["clause_text", "risk_level"]].copy()
    df["clause_text"] = df["clause_text"].fillna("").astype(str).str.strip()
    df["risk_level"] = df["risk_level"].map(_normalize_label)

    df = df[(df["clause_text"].str.len() > 0) & (df["risk_level"].isin(ALLOWED_LABELS))]
    if df.empty:
        raise SystemExit("No training rows after cleaning (check labels + clause_text)")

    return df


def train_and_eval(df: pd.DataFrame, seed: int = 42) -> Pipeline:
    X = df["clause_text"].tolist()
    y = df["risk_level"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=seed,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=80_000,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n=== Holdout Classification Report (20%) ===")
    print(classification_report(y_test, y_pred, digits=3))

    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("Graphs-for-NLP/data/base_contract_clauses.csv"),
        help="Path to training CSV (default: Graphs-for-NLP/data/base_contract_clauses.csv)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("Graphs-for-NLP/data/risk_model.pkl"),
        help="Output path for trained model (default: Graphs-for-NLP/data/risk_model.pkl)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not args.data.exists():
        raise SystemExit(f"Training data not found: {args.data}")

    df = _load_training_df(args.data)
    print(f"Loaded training rows: {len(df):,}")

    model = train_and_eval(df, seed=args.seed)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "wb") as f:
        pickle.dump(model, f)

    print(f"\nSaved model to: {args.out}")


if __name__ == "__main__":
    main()
