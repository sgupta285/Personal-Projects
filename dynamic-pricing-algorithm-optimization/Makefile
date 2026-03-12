PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/bootstrap.py

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

clean:
	rm -f data/raw/*.csv data/processed/*.csv data/*.db
	rm -f artifacts/*.json artifacts/*.csv artifacts/*.html artifacts/*.png
	mkdir -p artifacts dashboard/output data/raw data/processed
	touch artifacts/.gitkeep dashboard/output/.gitkeep
