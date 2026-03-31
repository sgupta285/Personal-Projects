.PHONY: install test format run-api run-worker seed

install:
	pip install -e .[dev]
	playwright install chromium

test:
	pytest

format:
	ruff format .
	ruff check . --fix

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	python -m app.worker

seed:
	python scripts/demo_seed.py
