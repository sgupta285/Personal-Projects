.PHONY: install dev worker test sample docker-up docker-down

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload

worker:
	python -m app.worker

test:
	pytest

sample:
	python scripts/create_sample_document.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down
