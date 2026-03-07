# Architecture Overview

## Core Components

### FastAPI layer
Provides operational endpoints for health, generation, retrieval, and evaluation.

### Inference layer
Abstracts two serving modes:
- `hf-local` for simple local execution
- `vllm-openai` for high-throughput OpenAI-compatible serving

### Retrieval layer
Uses a TF-IDF baseline retriever for a lightweight, transparent retrieval benchmark.

### Evaluation layer
Runs question-answer evaluation against a JSONL dataset and logs metrics to MLflow.

### Tracking layer
MLflow stores run parameters, metrics, and artifacts for repeatable comparisons.

## Why this design works

- easy to demo locally
- easy to swap model serving backends
- simple enough to understand quickly
- structured enough to feel production-ready
