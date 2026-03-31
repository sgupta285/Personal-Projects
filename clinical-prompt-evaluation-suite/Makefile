.PHONY: install run seed test export-demo

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

seed:
	python scripts/seed_demo.py

test:
	pytest -q

export-demo:
	python scripts/export_excel_report.py
