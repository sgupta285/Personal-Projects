from dataclasses import dataclass
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.io_utils import load_jsonl


@dataclass
class RetrievalResult:
    doc_id: str
    text: str
    score: float


class TfidfRetriever:
    def __init__(self, corpus_rows: List[Dict[str, Any]]) -> None:
        self.corpus_rows = corpus_rows
        self.texts = [row["text"] for row in corpus_rows]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.texts)

    @classmethod
    def from_path(cls, path: str) -> "TfidfRetriever":
        return cls(load_jsonl(path))

    def search(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix).flatten()
        top_idx = sims.argsort()[::-1][:top_k]
        results = []
        for idx in top_idx:
            row = self.corpus_rows[idx]
            results.append(RetrievalResult(doc_id=row["doc_id"], text=row["text"], score=float(sims[idx])))
        return results
