build:
	cmake -S . -B build
	cmake --build build

run: build
	./build/realtime_control --config examples/config/default.json --output data/logs/run.csv

test: build
	ctest --test-dir build --output-on-failure

analyze:
	python3 scripts/analyze_results.py --input data/logs/run.csv --output-dir docs/generated

clean:
	rm -rf build docs/generated data/logs/run.csv data/logs/summary.json
