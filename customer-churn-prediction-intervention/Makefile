PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/bootstrap.py

train:
	$(PYTHON) scripts/train_model.py

seed-db:
	$(PYTHON) scripts/seed_database.py

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	streamlit run dashboard/app.py

test:
	pytest

clean:
	rm -f data/raw/*.csv data/processed/*.csv data/*.db
	rm -f docs/screenshots/*.png
	rm -rf artifacts/*
	mkdir -p artifacts docs/screenshots
	touch artifacts/.gitkeep docs/screenshots/.gitkeep
