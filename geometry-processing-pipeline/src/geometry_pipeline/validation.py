from __future__ import annotations

import numpy as np

from .mesh import Mesh


def validate_mesh(mesh: Mesh) -> dict:
    tri = mesh.face_vertices()
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    degenerate_faces = int(np.sum(areas < 1e-10))
    min_bounds, max_bounds = mesh.bounds()
    extents = max_bounds - min_bounds
    return {
        "vertex_count": mesh.vertex_count,
        "face_count": mesh.face_count,
        "degenerate_faces": degenerate_faces,
        "surface_area": round(mesh.surface_area(), 6),
        "bbox_min": min_bounds.round(6).tolist(),
        "bbox_max": max_bounds.round(6).tolist(),
        "extents": extents.round(6).tolist(),
    }
