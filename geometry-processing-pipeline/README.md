# Geometry Processing Pipeline

A practical computational geometry project for loading meshes, validating and cleaning them, smoothing and simplifying geometry, slicing meshes into manufacturing-style layers, and benchmarking runtime on small and large sample models.

The repo is intentionally local-first. It uses Python and NumPy for the mesh pipeline, matplotlib for visualization, and a small pure-Python loader stack for ASCII OBJ and STL so the project can run without heavyweight geometry dependencies.

## What the project does

- loads ASCII OBJ and STL meshes
- validates topology and basic mesh quality signals
- removes duplicate vertices and degenerate faces
- recomputes normals
- applies Laplacian smoothing
- simplifies meshes with voxel-style vertex clustering
- slices meshes into Z layers and exports toolpath-style segments
- benchmarks cleanup, smoothing, simplification, and slicing
- produces before/after visuals and summary artifacts

## Repository layout

```text
geometry-processing-pipeline/
├── src/geometry_pipeline/
├── scripts/
├── data/input/
├── data/output/
├── docs/
├── benchmarks/
├── notebooks/
└── tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/run_pipeline.py --input data/input/sample_cube.obj --name cube
python scripts/run_pipeline.py --input data/input/sample_bracket.obj --name bracket
python scripts/run_benchmarks.py
python scripts/generate_visuals.py
pytest
```

## Main outputs

- cleaned and simplified meshes in `data/output/`
- slice segment exports in `data/output/`
- benchmark summary in `benchmarks/benchmark_results.csv`
- visuals in `artifacts/`
- methodology and findings in `docs/FINDINGS.md`

## Visual outputs

After running the scripts, the repo generates:

- original vs cleaned mesh visual
- original vs simplified mesh visual
- slice segment preview
- benchmark bar chart

## Design choices

This implementation focuses on reproducibility and readability rather than advanced CAD kernels. That makes it well suited for local experimentation, and extension into CNC or additive-manufacturing style workflows.

## License 

MIT
