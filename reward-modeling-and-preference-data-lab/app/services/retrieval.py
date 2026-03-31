from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.repository import PreferenceLabRepository


@dataclass
class RetrievalRow:
    example_id: int
    prompt_text: str
    task_type: str
    similarity: float
    top_candidate_labels: list[str]


class PreferenceExampleRetriever:
    def __init__(self, repository: PreferenceLabRepository) -> None:
        self.repository = repository

    def search(self, dataset_id: int, query: str, top_k: int = 5) -> list[RetrievalRow]:
        examples = self.repository.list_examples(dataset_id=dataset_id)
        if not examples:
            return []
        corpus = [self._compose_document(example) for example in examples]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(corpus)
        query_vector = vectorizer.transform([query])
        scores = cosine_similarity(query_vector, matrix)[0]
        order = np.argsort(scores)[::-1][:top_k]
        results: list[RetrievalRow] = []
        for idx in order:
            example = examples[idx]
            results.append(
                RetrievalRow(
                    example_id=example["id"],
                    prompt_text=example["prompt_text"],
                    task_type=example["task_type"],
                    similarity=round(float(scores[idx]), 4),
                    top_candidate_labels=[candidate["label"] for candidate in example["candidates"]],
                )
            )
        return results

    @staticmethod
    def _compose_document(example: dict) -> str:
        responses = " ".join(candidate["response_text"] for candidate in example["candidates"])
        context = " ".join(f"{key}: {value}" for key, value in example["context"].items())
        metadata = " ".join(f"{key}: {value}" for key, value in example["metadata"].items())
        return f"{example['prompt_text']} {responses} {context} {metadata}".strip()
