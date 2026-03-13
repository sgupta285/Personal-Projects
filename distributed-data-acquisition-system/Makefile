BUILD_DIR ?= build

configure:
	cmake -S . -B $(BUILD_DIR)

build: configure
	cmake --build $(BUILD_DIR) -j

test: build
	ctest --test-dir $(BUILD_DIR) --output-on-failure

run-baseline: build
	./$(BUILD_DIR)/daq_acquire --scenario baseline

run-benchmarks: build
	python3 scripts/run_benchmarks.py

analyze:
	python3 scripts/analyze_results.py

replay: build
	./$(BUILD_DIR)/daq_replay --input data/generated/baseline_stream.bin --max-messages 20

clean:
	rm -rf $(BUILD_DIR) data/generated/* results/*
