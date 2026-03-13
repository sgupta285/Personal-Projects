from __future__ import annotations

import numpy as np

from .mesh import Mesh


def _segment_intersections(triangle: np.ndarray, z: float) -> list[np.ndarray]:
    points = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        p1 = triangle[i]
        p2 = triangle[j]
        z1, z2 = p1[2], p2[2]
        if (z1 <= z <= z2) or (z2 <= z <= z1):
            if abs(z2 - z1) < 1e-12:
                continue
            t = (z - z1) / (z2 - z1)
            if 0 <= t <= 1:
                points.append(p1 + t * (p2 - p1))
    dedup = []
    for p in points:
        if not any(np.allclose(p, q, atol=1e-8) for q in dedup):
            dedup.append(p)
    return dedup


def slice_mesh(mesh: Mesh, layer_height: float = 0.2) -> list[dict]:
    min_bounds, max_bounds = mesh.bounds()
    levels = np.arange(min_bounds[2] + layer_height, max_bounds[2], layer_height)
    slices = []
    tri = mesh.face_vertices()
    for z in levels:
        segments = []
        for triangle in tri:
            pts = _segment_intersections(triangle, float(z))
            if len(pts) == 2:
                segments.append([[float(pts[0][0]), float(pts[0][1])], [float(pts[1][0]), float(pts[1][1])]])
        slices.append({"z": round(float(z), 6), "segments": segments})
    return slices
