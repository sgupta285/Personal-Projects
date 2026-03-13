from __future__ import annotations

import numpy as np

from .mesh import Mesh


def laplacian_smooth(mesh: Mesh, iterations: int = 5, alpha: float = 0.35) -> Mesh:
    out = mesh.copy()
    neighbors = out.adjacency()
    for _ in range(iterations):
        updated = out.vertices.copy()
        for i, nbrs in enumerate(neighbors):
            if not nbrs:
                continue
            centroid = out.vertices[list(nbrs)].mean(axis=0)
            updated[i] = (1 - alpha) * out.vertices[i] + alpha * centroid
        out.vertices = updated
    return out


def voxel_simplify(mesh: Mesh, voxel_size: float = 0.2) -> Mesh:
    min_bounds, _ = mesh.bounds()
    voxel_keys = np.floor((mesh.vertices - min_bounds) / voxel_size).astype(int)
    unique_keys, inverse = np.unique(voxel_keys, axis=0, return_inverse=True)
    new_vertices = np.zeros((len(unique_keys), 3), dtype=float)
    counts = np.zeros(len(unique_keys), dtype=int)
    for idx, cluster in enumerate(inverse):
        new_vertices[cluster] += mesh.vertices[idx]
        counts[cluster] += 1
    new_vertices /= counts[:, None]
    new_faces = inverse[mesh.faces]
    distinct = np.apply_along_axis(lambda row: len(set(map(int, row))) == 3, 1, new_faces)
    return Mesh(new_vertices, new_faces[distinct])
