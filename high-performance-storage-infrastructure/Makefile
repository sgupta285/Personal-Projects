PYTHON ?= python3
export PYTHONPATH=src

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/bootstrap.py

benchmark:
	$(PYTHON) scripts/run_benchmarks.py

resilience:
	$(PYTHON) scripts/run_resilience.py

test:
	pytest -q

clean:
	rm -rf data/store/benchmarks
	rm -f data/benchmarks/*.csv data/benchmarks/*.json
	rm -f data/reports/*.html data/reports/*.png data/reports/*.md
	mkdir -p data/store data/benchmarks data/reports
