from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    GenerateRequest,
    GenerateResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrievedDocument,
)
from app.eval.pipeline import EvaluationPipeline
from app.retrieval.index import TfidfRetriever
from app.services.inference import get_inference_client

router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "default_backend": settings.default_backend,
        "default_model": settings.default_model,
    }


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    client = get_inference_client(request.backend, request.model, request.base_url)
    result = client.generate(
        request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
    )
    return GenerateResponse(**result)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    corpus_path = request.corpus_path or get_settings().retrieval_corpus_path
    retriever = TfidfRetriever.from_path(corpus_path)
    results = retriever.search(request.query, top_k=request.top_k)
    return RetrieveResponse(results=[RetrievedDocument(**r.__dict__) for r in results])


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    retrieval_corpus_path = request.retrieval_corpus_path or get_settings().retrieval_corpus_path
    try:
        pipeline = EvaluationPipeline(
            dataset_path=request.dataset_path,
            retrieval_corpus_path=retrieval_corpus_path,
            backend=request.backend,
            model=request.model,
            base_url=request.base_url,
            experiment_name=request.experiment_name,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            retrieval_top_k=request.retrieval_top_k,
        )
        result = pipeline.run()
        return EvaluateResponse(
            run_id=result["run_id"],
            metrics=result["metrics"],
            output_path=result["output_path"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
