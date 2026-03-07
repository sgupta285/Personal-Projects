import time
from typing import Any, Dict

import httpx
from transformers import pipeline

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseInferenceClient:
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError


class HuggingFaceLocalClient(BaseInferenceClient):
    def __init__(self, model: str) -> None:
        self.model_name = model
        self.generator = pipeline("text-generation", model=model)

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        max_new_tokens = kwargs.get("max_new_tokens", 64)
        temperature = kwargs.get("temperature", 0.2)
        top_p = kwargs.get("top_p", 0.95)
        started = time.perf_counter()
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            return_full_text=False,
        )
        latency = time.perf_counter() - started
        text = outputs[0]["generated_text"]
        tokens_generated = max(1, len(text.split()))
        return {
            "text": text,
            "latency_seconds": latency,
            "tokens_generated": tokens_generated,
            "tokens_per_second": tokens_generated / max(latency, 1e-6),
            "raw": outputs,
        }


class VLLMOpenAIClient(BaseInferenceClient):
    def __init__(self, model: str, base_url: str) -> None:
        self.model_name = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        max_tokens = kwargs.get("max_new_tokens", 64)
        temperature = kwargs.get("temperature", 0.2)
        top_p = kwargs.get("top_p", 0.95)
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        started = time.perf_counter()
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{self.base_url}/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        latency = time.perf_counter() - started
        text = data["choices"][0]["text"]
        usage = data.get("usage", {})
        completion_tokens = usage.get("completion_tokens", max(1, len(text.split())))
        return {
            "text": text,
            "latency_seconds": latency,
            "tokens_generated": completion_tokens,
            "tokens_per_second": completion_tokens / max(latency, 1e-6),
            "raw": data,
        }


def get_inference_client(backend: str, model: str, base_url: str | None = None) -> BaseInferenceClient:
    if backend == "hf-local":
        logger.info("Creating Hugging Face local inference client", extra={"extra_fields": {"model": model}})
        return HuggingFaceLocalClient(model=model)
    if backend == "vllm-openai":
        if not base_url:
            raise ValueError("base_url is required when backend='vllm-openai'")
        logger.info("Creating vLLM OpenAI client", extra={"extra_fields": {"model": model, "base_url": base_url}})
        return VLLMOpenAIClient(model=model, base_url=base_url)
    raise ValueError(f"Unsupported backend: {backend}")
