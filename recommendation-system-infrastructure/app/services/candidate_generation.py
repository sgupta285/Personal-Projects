from __future__ import annotations

from pathlib import Path

import numpy as np

from app.core.config import settings

try:
    import faiss  # type: ignore
except Exception:
    faiss = None


class CandidateGenerator:
    def __init__(self) -> None:
        self.user_embeddings: np.ndarray | None = None
        self.item_embeddings: np.ndarray | None = None
        self.user_ids: list[str] = []
        self.item_ids: list[str] = []
        self.index = None

    def load(self) -> None:
        self.user_embeddings = np.load(Path(settings.user_embeddings_path))
        self.item_embeddings = np.load(Path(settings.item_embeddings_path))
        self.user_ids = Path("data/processed/user_ids.txt").read_text().splitlines()
        self.item_ids = Path("data/processed/item_ids.txt").read_text().splitlines()
        if faiss is not None:
            dimension = self.item_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(self.item_embeddings.astype(np.float32))

    def user_index(self, user_id: str) -> int:
        return self.user_ids.index(user_id)

    def item_index(self, item_id: str) -> int:
        return self.item_ids.index(item_id)

    def similar_items(self, item_id: str, top_k: int) -> list[tuple[str, float]]:
        idx = self.item_index(item_id)
        query = self.item_embeddings[idx]
        return self._search(query, top_k + 1, exclude={idx})

    def for_user(self, user_id: str, top_k: int) -> list[tuple[str, float]]:
        idx = self.user_index(user_id)
        query = self.user_embeddings[idx]
        return self._search(query, top_k)

    def _search(self, query: np.ndarray, top_k: int, exclude: set[int] | None = None) -> list[tuple[str, float]]:
        exclude = exclude or set()
        if self.index is not None:
            scores, indices = self.index.search(query.reshape(1, -1).astype(np.float32), top_k + len(exclude))
            raw = zip(indices[0].tolist(), scores[0].tolist())
        else:
            scores = self.item_embeddings @ query
            order = np.argsort(scores)[::-1][: top_k + len(exclude)]
            raw = ((int(i), float(scores[i])) for i in order)
        results = []
        for idx, score in raw:
            if idx in exclude:
                continue
            results.append((self.item_ids[idx], float(score)))
            if len(results) >= top_k:
                break
        return results
