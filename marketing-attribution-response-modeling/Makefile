PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/bootstrap.py

test:
	pytest

clean:
	rm -f data/raw/*.csv data/processed/*.csv data/*.db reports/*.png reports/*.json dashboard/index.html docs/STAKEHOLDER_SUMMARY.md
