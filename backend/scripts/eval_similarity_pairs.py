"""Evaluate similarity threshold against labeled pairs.

Reads Graphs-for-NLP/data/pairs_to_label.csv (expects is_similar = 0/1).
Compares labels to a thresholded similarity score.

Usage:
  /home/sumit/Documents/NLP Project/.venv/bin/python backend/scripts/eval_similarity_pairs.py

Optional:
  ... eval_similarity_pairs.py --input Graphs-for-NLP/data/pairs_to_label.csv --threshold 0.75
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix


def main() -> None:
    start_time = time.perf_counter()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("/home/sumit/Documents/NLP Project/Graphs-for-NLP/data/pairs_auto_labeled.csv"),
        help="CSV with labeled pairs (is_similar = 0/1)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Similarity threshold used to classify pairs",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    df = pd.read_csv(args.input)
    if "is_similar" not in df.columns:
        raise SystemExit("Missing required column 'is_similar'")
    if "similarity" not in df.columns:
        raise SystemExit("Missing required column 'similarity'")

    def _coerce_label(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        if isinstance(val, (int, bool)):
            return int(val)
        s = str(val).strip().lower()
        if s in {"1", "yes", "y", "true", "t"}:
            return 1
        if s in {"0", "no", "n", "false", "f"}:
            return 0
        return None

    df["_label"] = df["is_similar"].map(_coerce_label)
    df = df[df["_label"].isin([0, 1])].copy()
    if df.empty:
        raise SystemExit("No labeled rows found. Fill is_similar with 0/1 (or yes/no).")

    y_true = df["_label"].astype(int)
    y_pred = (df["similarity"].fillna(0) >= args.threshold).astype(int)

    print(f"Rows used: {len(df)}")
    print(f"Threshold: {args.threshold}")
    print("\nConfusion matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification report:")
    print(classification_report(y_true, y_pred, digits=3))
    elapsed_seconds = time.perf_counter() - start_time
    print(f"\nElapsed time: {elapsed_seconds:.3f} seconds")


if __name__ == "__main__":
    main()
