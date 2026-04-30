from __future__ import annotations

from itertools import combinations

import networkx as nx
import numpy as np

from schemas.contracts import Clause, GraphEdge
from services.model_singleton import embed


def build_document_graph(
    clauses: list[Clause],
    similarity_threshold: float = 0.75,
) -> tuple[nx.Graph, list[GraphEdge], list[list[float]]]:
    if not clauses:
        return nx.Graph(), [], []

    clause_texts = [c.text[:1200] for c in clauses]
    vectors = embed(clause_texts).tolist()

    graph = nx.Graph()
    for clause in clauses:
        graph.add_node(clause.index, label=clause.label, text=clause.text)

    # Vectors are normalized, so matrix multiplication yields cosine similarity.
    mat = np.asarray(vectors, dtype=np.float32)
    sim_matrix = mat @ mat.T

    edges: list[GraphEdge] = []
    for i, j in combinations(range(len(clauses)), 2):
        similarity = float(sim_matrix[i, j])
        if similarity >= similarity_threshold:
            source = clauses[i].index
            target = clauses[j].index
            graph.add_edge(source, target, similarity=similarity)
            edges.append(
                GraphEdge(
                    source_index=source,
                    target_index=target,
                    similarity=similarity,
                )
            )

    # Add sequential edges to connect all clauses
    for i in range(len(clauses) - 1):
        source = clauses[i].index
        target = clauses[i + 1].index
        graph.add_edge(source, target, similarity=0.1)
        edges.append(
            GraphEdge(
                source_index=source,
                target_index=target,
                similarity=0.1,
            )
        )

    return graph, edges, vectors


