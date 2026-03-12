PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

bootstrap:
	$(PYTHON) scripts/render_assets.py

test:
	pytest

run-gateway:
	uvicorn gateway_service.main:app --app-dir services/gateway --reload --port 8000

run-catalog:
	uvicorn catalog_service.main:app --app-dir services/catalog --reload --port 8001

run-orders:
	uvicorn orders_service.main:app --app-dir services/orders --reload --port 8002

compose-up:
	docker compose up --build

compose-down:
	docker compose down
