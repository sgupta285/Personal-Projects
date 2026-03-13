# Geometry Pipeline Analysis Notebook Notes

This repository uses plain Python scripts for portability, but this file documents the same analysis flow you would typically run in a notebook:

1. load `benchmarks/benchmark_results.csv`
2. compare total runtime and memory by mesh
3. inspect `data/output/*_summary.json` for face-count changes
4. inspect `artifacts/*_cleanup.png` and `artifacts/*_simplified.png`
5. inspect `artifacts/*_slices.png` to verify that the sliced geometry still matches the intended shape

A notebook can be added later without changing the pipeline code.
