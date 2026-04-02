.PHONY: setup run test seed benchmark smoke cpp

setup:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

seed:
	python scripts/seed_demo.py

benchmark:
	python scripts/benchmark_ingest.py --records 5000

smoke:
	bash scripts/smoke_test.sh

cpp:
	cmake -S cpp -B cpp/build && cmake --build cpp/build
