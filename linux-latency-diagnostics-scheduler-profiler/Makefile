.PHONY: install test demo lint package

install:
	python3 -m pip install -e .[dev]

test:
	pytest -q

demo:
	latdiag demo --output-dir artifacts/demo

package:
	python3 -m zipfile -c linux-latency-diagnostics-scheduler-profiler.zip .
