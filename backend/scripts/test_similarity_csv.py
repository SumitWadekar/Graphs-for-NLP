"""Build clause similarity edges from a CSV (NO risk model).

Input CSV must include a `clause_text` column.
Outputs a summary and (optionally) a CSV of similar clause pairs.

Usage:
  /home/sumit/Documents/NLP Project/.venv/bin/python backend/scripts/test_similarity_csv.py --input path/to/file.csv

Examples:
  # Use the base dataset and save pairs
  ... test_similarity_csv.py --input Graphs-for-NLP/data/base_contract_clauses.csv --output pairs.csv --threshold 0.80
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running this script directly from backend/scripts
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.model_singleton import embed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="CSV file with clause_text column")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Similarity threshold (0-1). Default: 0.75",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Optional limit for quick testing (0 = no limit)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Embedding batch size (default: 64)",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=512,
        help="Similarity block size (default: 512)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save similar pairs as CSV",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Do not include clause text in output CSV (smaller files)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    nrows = args.max_rows if args.max_rows and args.max_rows > 0 else None
    df = pd.read_csv(args.input, usecols=["clause_text"], nrows=nrows)
    if "clause_text" not in df.columns:
        raise SystemExit(
            f"Missing required column 'clause_text' in {args.input}.\n"
            f"Columns found: {list(df.columns)}"
        )

    texts = df["clause_text"].fillna("").astype(str).str.strip().tolist()
    total = len(texts)

    print(f"Rows: {total:,}")
    print(f"Similarity threshold: {args.threshold}")
    print(f"Embedding batch size: {args.batch_size}")
    print(f"Similarity block size: {args.block_size}")

    # Embed in batches to limit peak RAM
    embeddings: list[np.ndarray] = []
    for i in range(0, total, args.batch_size):
        batch = texts[i : i + args.batch_size]
        emb = embed(batch)
        embeddings.append(np.asarray(emb, dtype=np.float32))
    vectors = np.vstack(embeddings) if embeddings else np.empty((0, 0), dtype=np.float32)

    out_writer = None
    out_f = None
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        out_f = open(args.output, "w", newline="", encoding="utf-8")
        out_writer = csv.writer(out_f)
        if args.no_text:
            out_writer.writerow(["source_index", "target_index", "similarity"])
        else:
            out_writer.writerow([
                "source_index",
                "target_index",
                "similarity",
                "source_text",
                "target_text",
            ])

    edge_count = 0
    bs = max(1, args.block_size)

    for i in range(0, total, bs):
        vec_i = vectors[i : i + bs]
        if vec_i.size == 0:
            continue
        for j in range(i, total, bs):
            vec_j = vectors[j : j + bs]
            if vec_j.size == 0:
                continue

            sim = vec_i @ vec_j.T
            if i == j:
                mask = np.triu(sim, k=1) >= args.threshold
            else:
                mask = sim >= args.threshold

            count = int(mask.sum())
            if count == 0:
                continue
            edge_count += count

            if out_writer is not None:
                idxs = np.argwhere(mask)
                for a, b in idxs:
                    src = i + int(a)
                    tgt = j + int(b)
                    score = float(sim[a, b])
                    if args.no_text:
                        out_writer.writerow([src, tgt, score])
                    else:
                        out_writer.writerow([src, tgt, score, texts[src], texts[tgt]])

    if out_f is not None:
        out_f.close()

    print(f"Edges found: {edge_count:,}")
    if args.output is not None:
        print(f"Wrote pairs CSV: {args.output}")


if __name__ == "__main__":
    main()
