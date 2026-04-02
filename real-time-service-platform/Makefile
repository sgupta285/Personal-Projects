PYTHON ?= python3
PIP ?= pip3

install:
	cd backend && $(PIP) install -r requirements.txt

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	cd backend && $(PYTHON) scripts/seed.py

test:
	cd backend && pytest -q

smoke:
	cd backend && $(PYTHON) scripts/smoke_test.py

bench:
	cd backend && $(PYTHON) scripts/benchmark.py
