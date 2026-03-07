.PHONY: install dev api eval test lint format mlflow

install:
	pip install -e .

dev:
	pip install -e .[dev]

api:
	uvicorn app.main:app --reload --port 8000

mlflow:
	mlflow ui --backend-store-uri ./artifacts/mlruns --port 5001

eval:
	python scripts/run_eval.py --dataset data/sample/qa_eval.jsonl --retrieval-corpus data/sample/retrieval_corpus.jsonl --backend hf-local --model sshleifer/tiny-gpt2 --experiment-name llm-eval-demo

test:
	pytest

lint:
	ruff check .

format:
	black .
