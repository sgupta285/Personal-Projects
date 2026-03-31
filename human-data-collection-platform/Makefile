.PHONY: run seed test lint frontend

run:
	uvicorn app.main:app --reload

seed:
	python scripts/seed_demo.py

test:
	pytest

frontend:
	cd frontend && npm install && npm run dev
