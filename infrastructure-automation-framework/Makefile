PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .

demo:
	$(PYTHON) -m infraforge.cli demo --output examples/generated

test:
	pytest
