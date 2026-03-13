from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
import tracemalloc

from .io import load_mesh
from .pipeline import process_mesh


@dataclass
class BenchmarkResult:
    name: str
    vertex_count: int
    face_count: int
    cleanup_seconds: float
    smoothing_seconds: float
    simplification_seconds: float
    slicing_seconds: float
    total_seconds: float
    peak_memory_mb: float
    simplified_vertices: int
    simplified_faces: int
    layer_count: int


def run_benchmark(path, name: str, voxel_size: float = 0.2, layer_height: float = 0.2) -> BenchmarkResult:
    mesh = load_mesh(path)
    tracemalloc.start()
    start = perf_counter()
    result = process_mesh(mesh, voxel_size=voxel_size, layer_height=layer_height)
    total_seconds = perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return BenchmarkResult(
        name=name,
        vertex_count=mesh.vertex_count,
        face_count=mesh.face_count,
        cleanup_seconds=result.timings["cleanup_seconds"],
        smoothing_seconds=result.timings["smoothing_seconds"],
        simplification_seconds=result.timings["simplification_seconds"],
        slicing_seconds=result.timings["slicing_seconds"],
        total_seconds=total_seconds,
        peak_memory_mb=peak / (1024 * 1024),
        simplified_vertices=result.simplified.vertex_count,
        simplified_faces=result.simplified.face_count,
        layer_count=len(result.slices),
    )
