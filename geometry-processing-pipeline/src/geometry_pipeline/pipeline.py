from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .cleanup import repair_mesh
from .mesh import Mesh
from .ops import laplacian_smooth, voxel_simplify
from .slicing import slice_mesh
from .validation import validate_mesh


@dataclass
class PipelineResult:
    original: Mesh
    cleaned: Mesh
    smoothed: Mesh
    simplified: Mesh
    slices: list[dict]
    timings: dict
    validations: dict


def process_mesh(mesh: Mesh, smooth_iterations: int = 1, alpha: float = 0.12, voxel_size: float = 0.2, layer_height: float = 0.2) -> PipelineResult:
    timings = {}
    validations = {"original": validate_mesh(mesh)}

    t0 = perf_counter()
    cleaned = repair_mesh(mesh)
    timings["cleanup_seconds"] = perf_counter() - t0
    validations["cleaned"] = validate_mesh(cleaned)

    t0 = perf_counter()
    smoothed = laplacian_smooth(cleaned, iterations=smooth_iterations, alpha=alpha)
    timings["smoothing_seconds"] = perf_counter() - t0
    validations["smoothed"] = validate_mesh(smoothed)

    t0 = perf_counter()
    simplified = voxel_simplify(smoothed, voxel_size=voxel_size)
    timings["simplification_seconds"] = perf_counter() - t0
    validations["simplified"] = validate_mesh(simplified)

    t0 = perf_counter()
    slices = slice_mesh(simplified, layer_height=layer_height)
    timings["slicing_seconds"] = perf_counter() - t0

    return PipelineResult(
        original=mesh,
        cleaned=cleaned,
        smoothed=smoothed,
        simplified=simplified,
        slices=slices,
        timings=timings,
        validations=validations,
    )
