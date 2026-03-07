from __future__ import annotations

from typing import Iterable, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingRelevanceScorer:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def score(self, prediction: str, reference: str) -> float:
        embeddings = self.model.encode([prediction, reference], normalize_embeddings=True)
        return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])


def recall_at_k(retrieved_doc_ids: List[str], gold_doc_id: str, k: int) -> float:
    return 1.0 if gold_doc_id in retrieved_doc_ids[:k] else 0.0


def reciprocal_rank(retrieved_doc_ids: List[str], gold_doc_id: str) -> float:
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id == gold_doc_id:
            return 1.0 / rank
    return 0.0


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return float(np.mean(values)) if values else 0.0
