"""Auto-label pairs based on a similarity threshold.

Usage:
  python3 auto_label_pairs.py --input ../../data/pairs_to_label.csv --output ../../data/pairs_auto_labeled.csv --threshold 0.75
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.75)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    with args.input.open("r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header")
        fieldnames = list(reader.fieldnames)
        if "is_similar" not in fieldnames:
            fieldnames.append("is_similar")

        rows = []
        for row in reader:
            sim_raw = row.get("similarity", "")
            try:
                sim = float(sim_raw)
            except Exception:
                sim = 0.0
            row["is_similar"] = "1" if sim >= args.threshold else "0"
            rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote auto-labeled file: {args.output}")


if __name__ == "__main__":
    main()
