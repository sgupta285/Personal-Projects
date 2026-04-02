setup:
	python -m pip install -r requirements.txt

run-api:
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

seed:
	python scripts/seed_samples.py

smoke:
	python scripts/smoke_test.py

benchmark:
	python scripts/benchmark.py

test:
	pytest

package-cpp:
	g++ -O2 -std=c++17 cpp/frame_budget_planner.cpp -o cpp/frame_budget_planner
