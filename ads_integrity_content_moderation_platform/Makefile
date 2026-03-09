PYTHON ?= python3

.PHONY: install api worker train-model seed test lint

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

api:
	PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	PYTHONPATH=backend $(PYTHON) -m worker.main

train-model:
	PYTHONPATH=backend $(PYTHON) scripts/train_classifier.py

seed:
	$(PYTHON) scripts/seed_ads.py

test:
	PYTHONPATH=backend pytest -q
