.PHONY: test smoke benchmark run

test:
	pytest -q

smoke:
	python scripts/smoke_test.py

benchmark:
	python scripts/benchmark.py --events 1500 --concurrency 8

run:
	uvicorn rtdp.api:app --app-dir src --host 0.0.0.0 --port 8000
