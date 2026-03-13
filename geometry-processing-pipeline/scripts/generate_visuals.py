from __future__ import annotations

from pathlib import Path
import csv

from geometry_pipeline.io import load_mesh
from geometry_pipeline.pipeline import process_mesh
from geometry_pipeline.visualize import save_benchmark_chart, save_mesh_comparison, save_slice_preview


def main() -> None:
    artifacts = Path('artifacts')
    artifacts.mkdir(parents=True, exist_ok=True)

    cube = load_mesh('data/input/sample_cube.obj')
    cube_result = process_mesh(cube, voxel_size=0.25, layer_height=0.2)
    save_mesh_comparison(cube_result.original, cube_result.cleaned, artifacts / 'cube_cleanup.png', 'Original cube', 'Cleaned cube')
    save_mesh_comparison(cube_result.original, cube_result.simplified, artifacts / 'cube_simplified.png', 'Original cube', 'Simplified cube')
    save_slice_preview(cube_result.slices, artifacts / 'cube_slices.png')

    bracket = load_mesh('data/input/sample_bracket.obj')
    bracket_result = process_mesh(bracket, voxel_size=0.3, layer_height=0.2)
    save_mesh_comparison(bracket_result.original, bracket_result.cleaned, artifacts / 'bracket_cleanup.png', 'Original bracket', 'Cleaned bracket')
    save_mesh_comparison(bracket_result.original, bracket_result.simplified, artifacts / 'bracket_simplified.png', 'Original bracket', 'Simplified bracket')
    save_slice_preview(bracket_result.slices, artifacts / 'bracket_slices.png')

    rows = []
    with open('benchmarks/benchmark_results.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['total_seconds'] = float(row['total_seconds'])
            row['peak_memory_mb'] = float(row['peak_memory_mb'])
            rows.append(row)
    save_benchmark_chart(rows, artifacts / 'benchmark_summary.png')
    print('Visuals written to artifacts/')


if __name__ == '__main__':
    main()
