"""Generate a labeled-pairs CSV for manual similarity evaluation.

Creates a CSV with 200 pairs by default:
- 100 high-similarity pairs (mined from a subset)
- 100 random pairs

Output file includes an empty `is_similar` column for manual labeling.

Usage:
  /home/sumit/Documents/NLP Project/.venv/bin/python backend/scripts/generate_pairs_to_label.py

Optional:
  ... generate_pairs_to_label.py --output Graphs-for-NLP/data/pairs_to_label.csv
"""

from __future__ import annotations

import argparse
import heapq
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("/home/sumit/Documents/NLP Project/Graphs-for-NLP/data/base_contract_clauses.csv"),
        help="Source CSV with clause_text column",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/home/sumit/Documents/NLP Project/Graphs-for-NLP/data/pairs_to_label.csv"),
        help="Output CSV path",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-clauses", type=int, default=2000)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--rand-k", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--block-size", type=int, default=256)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    # Allow backend imports when run from anywhere
    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from services.model_singleton import embed

    random.seed(args.seed)
    np.random.seed(args.seed)

    df = pd.read_csv(args.input, usecols=["clause_text"]).fillna("")
    texts = df["clause_text"].astype(str).str.strip().tolist()
    n_total = len(texts)

    indices = list(range(n_total))
    random.shuffle(indices)
    subset_idx = indices[: min(args.sample_clauses, n_total)]
    subset_texts = [texts[i] for i in subset_idx]

    # Embed subset in batches
    embs = []
    for i in range(0, len(subset_texts), args.batch_size):
        batch = subset_texts[i : i + args.batch_size]
        embs.append(np.asarray(embed(batch), dtype=np.float32))
    vecs = np.vstack(embs) if embs else np.empty((0, 0), dtype=np.float32)

    # Mine high-similarity pairs within subset
    heap: list[tuple[float, int, int]] = []
    bs = max(1, args.block_size)
    for i in range(0, len(subset_texts), bs):
        vi = vecs[i : i + bs]
        for j in range(i, len(subset_texts), bs):
            vj = vecs[j : j + bs]
            sim = vi @ vj.T
            mask = np.triu(sim, k=1) if i == j else sim

            flat = mask.ravel()
            if flat.size == 0:
                continue
            k_local = min(50, flat.size)
            idx = np.argpartition(flat, -k_local)[-k_local:]
            for idx_flat in idx:
                a = idx_flat // mask.shape[1]
                b = idx_flat % mask.shape[1]
                score = float(mask[a, b])
                if i == j and a >= b:
                    continue
                if len(heap) < args.top_k:
                    heapq.heappush(heap, (score, i + a, j + b))
                else:
                    if score > heap[0][0]:
                        heapq.heapreplace(heap, (score, i + a, j + b))

    high_pairs = sorted(heap, key=lambda x: x[0], reverse=True)

    # Random pairs from full dataset
    rand_pairs: set[tuple[int, int]] = set()
    while len(rand_pairs) < args.rand_k:
        a = random.randrange(n_total)
        b = random.randrange(n_total)
        if a == b:
            continue
        if a > b:
            a, b = b, a
        rand_pairs.add((a, b))

    rows = []
    for score, a, b in high_pairs:
        ai = subset_idx[a]
        bi = subset_idx[b]
        rows.append(
            {
                "pair_type": "high_sim",
                "index_a": ai,
                "index_b": bi,
                "similarity": score,
                "clause_a": texts[ai],
                "clause_b": texts[bi],
                "is_similar": "",
            }
        )
    for a, b in sorted(rand_pairs):
        rows.append(
            {
                "pair_type": "random",
                "index_a": a,
                "index_b": b,
                "similarity": "",
                "clause_a": texts[a],
                "clause_b": texts[b],
                "is_similar": "",
            }
        )

    out_df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} pairs to {args.output}")


if __name__ == "__main__":
    main()
