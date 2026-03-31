.PHONY: run seed test export-analysis

run:
	uvicorn app.main:app --reload

seed:
	python scripts/seed_demo.py

test:
	pytest -q

export-analysis:
	python scripts/run_analysis.py
