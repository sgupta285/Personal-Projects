from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    backend: str = Field(default="hf-local")
    model: str = Field(default="sshleifer/tiny-gpt2")
    base_url: Optional[str] = None
    max_new_tokens: int = 64
    temperature: float = 0.2
    top_p: float = 0.95


class GenerateResponse(BaseModel):
    text: str
    latency_seconds: float
    tokens_generated: int
    tokens_per_second: float
    raw: Dict[str, Any]


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3
    corpus_path: Optional[str] = None


class RetrievedDocument(BaseModel):
    doc_id: str
    text: str
    score: float


class RetrieveResponse(BaseModel):
    results: List[RetrievedDocument]


class EvaluateRequest(BaseModel):
    dataset_path: str
    retrieval_corpus_path: Optional[str] = None
    backend: str = "hf-local"
    model: str = "sshleifer/tiny-gpt2"
    base_url: Optional[str] = None
    experiment_name: str = "llm-eval-demo"
    max_new_tokens: int = 64
    temperature: float = 0.2
    top_p: float = 0.95
    retrieval_top_k: int = 3


class EvaluateResponse(BaseModel):
    run_id: str
    metrics: Dict[str, float]
    output_path: str
