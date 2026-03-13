from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class Mesh:
    vertices: np.ndarray
    faces: np.ndarray

    def copy(self) -> "Mesh":
        return Mesh(self.vertices.copy(), self.faces.copy())

    @property
    def vertex_count(self) -> int:
        return int(len(self.vertices))

    @property
    def face_count(self) -> int:
        return int(len(self.faces))

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        return self.vertices.min(axis=0), self.vertices.max(axis=0)

    def face_vertices(self) -> np.ndarray:
        return self.vertices[self.faces]

    def face_normals(self) -> np.ndarray:
        tri = self.face_vertices()
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        return normals / norms

    def surface_area(self) -> float:
        tri = self.face_vertices()
        areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        return float(areas.sum())

    def adjacency(self) -> list[set[int]]:
        neighbors = [set() for _ in range(self.vertex_count)]
        for face in self.faces:
            a, b, c = map(int, face)
            neighbors[a].update([b, c])
            neighbors[b].update([a, c])
            neighbors[c].update([a, b])
        return neighbors
