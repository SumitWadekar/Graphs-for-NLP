"""Predict/evaluate risk_level for a CSV file.

- Requires a model trained by backend/scripts/train_risk_model.py
- Input CSV should have a `clause_text` column.
- If the CSV also has a `risk_level` column, this script prints metrics.

Usage:
  /home/sumit/Documents/NLP Project/.venv/bin/python backend/scripts/test_risk_csv.py --input path/to/file.csv

Examples:
  # Evaluate against known labels (if column exists)
  ... test_risk_csv.py --input Graphs-for-NLP/data/base_contract_clauses.csv --max-rows 500

  # Save predictions to a new CSV
  ... test_risk_csv.py --input my_contract.csv --output my_contract_with_predictions.csv
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report


ALLOWED_LABELS = {"low", "medium", "high"}


def _normalize_label(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x).strip().lower()


def _load_model(model_path: Path):
    if not model_path.exists():
        raise SystemExit(
            f"Model not found: {model_path}\n"
            "Train it first with: backend/scripts/train_risk_model.py"
        )
    with open(model_path, "rb") as f:
        return pickle.load(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="CSV file to test")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("Graphs-for-NLP/data/risk_model.pkl"),
        help="Path to trained model (default: Graphs-for-NLP/data/risk_model.pkl)",
    )
    parser.add_argument(
        "--text-col",
        type=str,
        default="clause_text",
        help="Text column name (default: clause_text)",
    )
    parser.add_argument(
        "--label-col",
        type=str,
        default="risk_level",
        help="Optional ground-truth label column (default: risk_level)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save CSV with predictions",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Optional limit for quick testing (0 = no limit)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    df = pd.read_csv(args.input)
    if args.text_col not in df.columns:
        raise SystemExit(
            f"Missing required column '{args.text_col}' in {args.input}.\n"
            f"Columns found: {list(df.columns)}"
        )

    if args.max_rows and args.max_rows > 0:
        df = df.head(args.max_rows).copy()

    texts = df[args.text_col].fillna("").astype(str).str.strip().tolist()

    model = _load_model(args.model)
    preds = model.predict(texts)
    df["predicted_risk_level"] = preds

    print(f"Rows: {len(df):,}")
    print("Prediction counts:")
    print(df["predicted_risk_level"].value_counts(dropna=False).to_string())

    if args.label_col in df.columns:
        y_true = df[args.label_col].map(_normalize_label)
        mask = y_true.isin(ALLOWED_LABELS)
        if mask.any():
            print("\n=== Evaluation on rows with ground-truth risk_level ===")
            print(classification_report(y_true[mask], df.loc[mask, "predicted_risk_level"], digits=3))
        else:
            print(
                f"\nLabel column '{args.label_col}' exists, but no valid labels found. "
                f"Expected one of: {sorted(ALLOWED_LABELS)}"
            )
    else:
        print(f"\nNo label column '{args.label_col}' found; skipping metrics.")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.output, index=False)
        print(f"\nWrote: {args.output}")


if __name__ == "__main__":
    main()
