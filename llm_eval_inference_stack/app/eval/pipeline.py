from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import mlflow
import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger
from app.eval.metrics import EmbeddingRelevanceScorer, mean, recall_at_k, reciprocal_rank
from app.retrieval.index import TfidfRetriever
from app.services.inference import get_inference_client
from app.services.io_utils import load_jsonl, write_jsonl

logger = get_logger(__name__)


class EvaluationPipeline:
    def __init__(
        self,
        dataset_path: str,
        retrieval_corpus_path: str,
        backend: str,
        model: str,
        base_url: str | None,
        experiment_name: str,
        max_new_tokens: int = 64,
        temperature: float = 0.2,
        top_p: float = 0.95,
        retrieval_top_k: int = 3,
    ) -> None:
        self.dataset_path = dataset_path
        self.retrieval_corpus_path = retrieval_corpus_path
        self.backend = backend
        self.model = model
        self.base_url = base_url
        self.experiment_name = experiment_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.retrieval_top_k = retrieval_top_k
        settings = get_settings()
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)

    def run(self) -> Dict[str, Any]:
        rows = load_jsonl(self.dataset_path)
        retriever = TfidfRetriever.from_path(self.retrieval_corpus_path)
        client = get_inference_client(self.backend, self.model, self.base_url)
        relevance_scorer = EmbeddingRelevanceScorer(get_settings().embedding_model)

        detailed_rows: List[Dict[str, Any]] = []

        with mlflow.start_run(run_name=f"{self.backend}-{self.model.split('/')[-1]}") as run:
            mlflow.log_params(
                {
                    "dataset_path": self.dataset_path,
                    "retrieval_corpus_path": self.retrieval_corpus_path,
                    "backend": self.backend,
                    "model": self.model,
                    "base_url": self.base_url or "",
                    "max_new_tokens": self.max_new_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "retrieval_top_k": self.retrieval_top_k,
                }
            )

            for row in rows:
                query = row["question"]
                gold_doc_id = row["gold_doc_id"]
                reference_answer = row["reference_answer"]

                retrieved = retriever.search(query, top_k=self.retrieval_top_k)
                retrieved_doc_ids = [item.doc_id for item in retrieved]
                context = "\n\n".join([f"[{item.doc_id}] {item.text}" for item in retrieved])
                prompt = (
                    "Answer the question using the context below. Be concise and factual.\n\n"
                    f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
                )
                generation = client.generate(
                    prompt,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                relevance = relevance_scorer.score(generation["text"], reference_answer)
                row_result = {
                    "question_id": row["question_id"],
                    "question": query,
                    "gold_doc_id": gold_doc_id,
                    "reference_answer": reference_answer,
                    "retrieved_doc_ids": retrieved_doc_ids,
                    "prediction": generation["text"],
                    "latency_seconds": generation["latency_seconds"],
                    "tokens_generated": generation["tokens_generated"],
                    "tokens_per_second": generation["tokens_per_second"],
                    "recall_at_k": recall_at_k(retrieved_doc_ids, gold_doc_id, self.retrieval_top_k),
                    "reciprocal_rank": reciprocal_rank(retrieved_doc_ids, gold_doc_id),
                    "answer_relevance": relevance,
                }
                detailed_rows.append(row_result)

            df = pd.DataFrame(detailed_rows)
            metrics = {
                "avg_latency_seconds": mean(df["latency_seconds"].tolist()),
                "avg_tokens_generated": mean(df["tokens_generated"].tolist()),
                "avg_tokens_per_second": mean(df["tokens_per_second"].tolist()),
                f"retrieval_recall@{self.retrieval_top_k}": mean(df["recall_at_k"].tolist()),
                "retrieval_mrr": mean(df["reciprocal_rank"].tolist()),
                "avg_answer_relevance": mean(df["answer_relevance"].tolist()),
                "num_examples": float(len(df)),
            }
            mlflow.log_metrics(metrics)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("artifacts") / "eval_runs" / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)
            jsonl_path = output_dir / "detailed_results.jsonl"
            csv_path = output_dir / "detailed_results.csv"
            summary_path = output_dir / "summary_metrics.json"

            write_jsonl(str(jsonl_path), detailed_rows)
            df.to_csv(csv_path, index=False)
            pd.Series(metrics).to_json(summary_path, indent=2)

            mlflow.log_artifact(str(jsonl_path))
            mlflow.log_artifact(str(csv_path))
            mlflow.log_artifact(str(summary_path))

            logger.info(
                "Evaluation completed",
                extra={
                    "extra_fields": {
                        "run_id": run.info.run_id,
                        "metrics": metrics,
                        "output_dir": str(output_dir),
                    }
                },
            )

            return {
                "run_id": run.info.run_id,
                "metrics": metrics,
                "output_path": str(output_dir),
                "rows": detailed_rows,
            }
