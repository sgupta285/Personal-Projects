PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

generate-data:
	$(PYTHON) scripts/generate_sample_data.py

run-pipeline:
	$(PYTHON) scripts/run_pipeline.py

benchmark:
	$(PYTHON) scripts/benchmark_pipeline.py

test:
	pytest

lint:
	ruff check src tests scripts
