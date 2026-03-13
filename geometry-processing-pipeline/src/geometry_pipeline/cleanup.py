from __future__ import annotations

import numpy as np

from .mesh import Mesh


def remove_duplicate_vertices(mesh: Mesh, tolerance: float = 1e-8) -> Mesh:
    rounded = np.round(mesh.vertices / tolerance).astype(np.int64)
    _, unique_idx, inverse = np.unique(rounded, axis=0, return_index=True, return_inverse=True)
    unique_vertices = mesh.vertices[np.sort(unique_idx)]
    sort_order = np.argsort(unique_idx)
    remap = sort_order[inverse]
    faces = remap[mesh.faces]
    return Mesh(unique_vertices, faces)


def remove_degenerate_faces(mesh: Mesh, area_eps: float = 1e-10) -> Mesh:
    tri = mesh.vertices[mesh.faces]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    keep = areas > area_eps
    return Mesh(mesh.vertices.copy(), mesh.faces[keep].copy())


def reindex_vertices(mesh: Mesh) -> Mesh:
    used = np.unique(mesh.faces.reshape(-1))
    mapping = {int(old): i for i, old in enumerate(used)}
    vertices = mesh.vertices[used]
    faces = np.vectorize(mapping.get)(mesh.faces)
    return Mesh(vertices, faces)


def repair_mesh(mesh: Mesh) -> Mesh:
    cleaned = remove_duplicate_vertices(mesh)
    cleaned = remove_degenerate_faces(cleaned)
    cleaned = reindex_vertices(cleaned)
    return cleaned
