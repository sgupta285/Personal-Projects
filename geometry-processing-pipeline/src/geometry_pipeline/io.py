from __future__ import annotations

from pathlib import Path
import numpy as np

from .mesh import Mesh


def load_mesh(path: str | Path) -> Mesh:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        return load_obj(path)
    if suffix == ".stl":
        return load_ascii_stl(path)
    raise ValueError(f"Unsupported format: {suffix}")


def load_obj(path: Path) -> Mesh:
    vertices = []
    faces = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('v '):
            _, x, y, z = line.split()[:4]
            vertices.append([float(x), float(y), float(z)])
        elif line.startswith('f '):
            parts = line.split()[1:]
            idx = []
            for part in parts[:3]:
                idx.append(int(part.split('/')[0]) - 1)
            faces.append(idx)
    return Mesh(np.asarray(vertices, dtype=float), np.asarray(faces, dtype=int))


def load_ascii_stl(path: Path) -> Mesh:
    vertices = []
    faces = []
    current = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith('vertex'):
            _, x, y, z = line.split()
            current.append([float(x), float(y), float(z)])
            if len(current) == 3:
                start = len(vertices)
                vertices.extend(current)
                faces.append([start, start + 1, start + 2])
                current = []
    return Mesh(np.asarray(vertices, dtype=float), np.asarray(faces, dtype=int))


def save_obj(mesh: Mesh, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for v in mesh.vertices:
        lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
    for f in mesh.faces:
        lines.append(f"f {int(f[0]) + 1} {int(f[1]) + 1} {int(f[2]) + 1}")
    path.write_text("\n".join(lines) + "\n")
