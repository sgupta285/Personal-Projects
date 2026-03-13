from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import csv

from geometry_pipeline.benchmark import run_benchmark


def main() -> None:
    benchmark_dir = Path('benchmarks')
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    inputs = [
        ('cube', 'data/input/sample_cube.obj'),
        ('bracket', 'data/input/sample_bracket.obj'),
        ('wave_panel', 'data/input/sample_wave_panel.obj'),
    ]
    rows = []
    for name, path in inputs:
        voxel_size = 0.22 if name == 'cube' else (0.28 if name == 'bracket' else 0.18)
        result = run_benchmark(path, name=name, voxel_size=voxel_size, layer_height=0.2)
        rows.append(asdict(result))
    with (benchmark_dir / 'benchmark_results.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print('Benchmark results written to benchmarks/benchmark_results.csv')


if __name__ == '__main__':
    main()
