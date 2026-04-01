PYTHON ?= python

install:
	$(PYTHON) -m pip install -e ".[dev]"

train:
	$(PYTHON) scripts/train_model.py

seed:
	$(PYTHON) scripts/seed_feature_store.py

run:
	uvicorn app.main:app --reload

test:
	pytest

benchmark:
	$(PYTHON) scripts/benchmark.py --requests 200 --concurrency 20
