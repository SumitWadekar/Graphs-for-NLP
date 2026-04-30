"""Evaluate labeled pairs without pandas/sklearn.

Usage:
  python3 eval_similarity_pairs_simple.py --input ../../data/pairs_auto_labeled.csv --threshold 0.75
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def safe_float(val: str) -> float:
    try:
        return float(val)
    except Exception:
        return 0.0


def safe_label(val: str):
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in {"1", "yes", "y", "true", "t"}:
        return 1
    if s in {"0", "no", "n", "false", "f"}:
        return 0
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.75)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    tp = tn = fp = fn = 0
    used = 0

    with args.input.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            y_true = safe_label(row.get("is_similar"))
            if y_true is None:
                continue
            sim = safe_float(row.get("similarity", ""))
            y_pred = 1 if sim >= args.threshold else 0
            used += 1
            if y_true == 1 and y_pred == 1:
                tp += 1
            elif y_true == 0 and y_pred == 0:
                tn += 1
            elif y_true == 0 and y_pred == 1:
                fp += 1
            elif y_true == 1 and y_pred == 0:
                fn += 1

    if used == 0:
        raise SystemExit("No labeled rows found. Fill is_similar with 0/1.")

    accuracy = (tp + tn) / used if used else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0

    print(f"Rows used: {used}")
    print(f"Threshold: {args.threshold}")
    print("\nConfusion matrix (rows=actual, cols=pred):")
    print(f"[[TN={tn}, FP={fp}],\n [FN={fn}, TP={tp}]]")
    print("\nMetrics:")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}  (Sensitivity)")
    print(f"Specificity: {specificity:.4f}")
    print(f"F1 Score:    {f1:.4f}")


if __name__ == "__main__":
    main()
