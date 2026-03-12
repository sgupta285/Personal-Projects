PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/bootstrap.py

dashboard:
	streamlit run dashboard/app.py

test:
	pytest
