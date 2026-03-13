install:
	python -m pip install --upgrade pip
	python -m pip install -e .

generate-samples:
	python scripts/generate_samples.py

pipeline:
	python scripts/run_pipeline.py --input data/input/sample_cube.obj --name cube
	python scripts/run_pipeline.py --input data/input/sample_bracket.obj --name bracket
	python scripts/run_pipeline.py --input data/input/sample_wave_panel.obj --name wave_panel

benchmarks:
	python scripts/run_benchmarks.py

visuals:
	python scripts/generate_visuals.py

test:
	pytest
