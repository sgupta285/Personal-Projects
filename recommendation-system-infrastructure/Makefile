PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements.txt

seed:
	$(PYTHON) scripts/generate_sample_data.py

train:
	$(PYTHON) -m app.ml.train

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

bench:
	$(PYTHON) scripts/benchmark_api.py

smoke:
	$(PYTHON) scripts/smoke_test.py
