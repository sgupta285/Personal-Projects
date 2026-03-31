# LLM Evaluation and Inference Stack

A production-style starter project for evaluating and serving transformer-based LLMs with:

- **Python** for orchestration
- **Hugging Face** for datasets, tokenizers, and local fallback inference
- **vLLM** for high-throughput OpenAI-compatible model serving
- **MLflow** for experiment tracking and reproducibility
- **FastAPI** for operational APIs and triggering evaluations

This project is designed to look and feel like a clean GitHub repository that an engineer would actually maintain. It supports:

- latency and throughput benchmarking
- retrieval quality evaluation (Recall@K, MRR)
- answer relevance scoring with embedding similarity
- prompt, checkpoint, and serving configuration comparison
- structured JSON logging
- MLflow experiment tracking
- FastAPI endpoints for search, evaluation, and health checks

## Repository Structure

```text
llm-eval-inference-stack/
├── app/
│   ├── api/
│   ├── core/
│   ├── eval/
│   ├── retrieval/
│   └── services/
├── configs/
├── data/
│   └── sample/
├── docs/
├── scripts/
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## What This Stack Does

### 1. Inference Benchmarking
Evaluates model behavior across prompts, decoding parameters, and model backends. Captures:
- request latency
- tokens per second
- end-to-end throughput
- per-run metadata for debugging and reproducibility

### 2. Retrieval Evaluation
Loads a small reference corpus and measures retrieval quality using:
- Recall@K
- MRR

### 3. Answer Relevance
Uses sentence-transformer embeddings to compare generated answers to reference answers and compute a semantic relevance score.

### 4. Experiment Tracking
Each evaluation run logs:
- parameters
- summary metrics
- artifacts
- detailed row-level output CSV/JSONL

## Quick Start

## 1) Create environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## 2) Start MLflow

```bash
mlflow ui --backend-store-uri ./artifacts/mlruns --port 5001
```

Then open `http://127.0.0.1:5001`

## 3) Start the FastAPI app

```bash
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs`

## 4) Run a local sample evaluation

This uses the lightweight local Hugging Face fallback by default.

```bash
python scripts/run_eval.py \
  --dataset data/sample/qa_eval.jsonl \
  --retrieval-corpus data/sample/retrieval_corpus.jsonl \
  --backend hf-local \
  --model sshleifer/tiny-gpt2 \
  --experiment-name llm-eval-demo
```

## 5) Run with vLLM

Start a vLLM server first. vLLM exposes an OpenAI-compatible server interface and defaults to `http://localhost:8000` unless configured otherwise. citeturn0search0turn0search4

Example:

```bash
python scripts/serve_vllm.py --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --port 8001
```

Then evaluate:

```bash
python scripts/run_eval.py \
  --dataset data/sample/qa_eval.jsonl \
  --retrieval-corpus data/sample/retrieval_corpus.jsonl \
  --backend vllm-openai \
  --base-url http://127.0.0.1:8001/v1 \
  --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --experiment-name llm-eval-vllm
```

## API Endpoints

- `GET /health` → service health and current config
- `POST /evaluate` → run an evaluation job synchronously
- `POST /retrieve` → retrieve top-k passages from the local corpus
- `POST /generate` → single inference call through configured backend

## Notes on vLLM

vLLM is included because it is the correct serving layer for realistic latency and throughput comparisons. Its OpenAI-compatible API server makes it easy to swap serving backends while keeping client code stable. citeturn0search0turn0search12

For meaningful throughput benchmarking, use a machine with a compatible GPU. The local Hugging Face backend is intended for development, unit testing, and low-resource demos.

## Notes on MLflow

MLflow is used here as the experiment system of record for runs, metrics, parameters, and artifacts. Recent MLflow documentation emphasizes experiment tracking and model or LLM evaluation workflows as first-class capabilities. citeturn0search1turn0search13

## Notes on FastAPI

The app uses a multi-file FastAPI structure with routers and typed request schemas, following the framework’s recommended modular application patterns. citeturn0search6turn0search10

## Example GitHub Upload Flow

```bash
git init
git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

## Future Extensions

- RAGAS or DeepEval integration
- judge-model scoring
- prompt registry and regression testing
- async job queue for long-running evaluations
- vector database integration for larger retrieval corpora

##License

MIT