from pathlib import Path
import math


def write_cube(path: Path) -> None:
    vertices = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),
        (0, 0, 0),
    ]
    faces = [
        (1, 2, 3), (1, 3, 4),
        (5, 6, 7), (5, 7, 8),
        (1, 5, 8), (1, 8, 4),
        (2, 6, 7), (2, 7, 3),
        (1, 2, 6), (1, 6, 5),
        (4, 3, 7), (4, 7, 8),
        (1, 1, 2),
    ]
    lines = [f"v {x} {y} {z}" for x, y, z in vertices] + [f"f {a} {b} {c}" for a, b, c in faces]
    path.write_text("\n".join(lines) + "\n")


def write_bracket(path: Path) -> None:
    vertices = [
        (0, 0, 0), (3, 0, 0), (3, 1, 0), (1, 1, 0), (1, 3, 0), (0, 3, 0),
        (0, 0, 1), (3, 0, 1), (3, 1, 1), (1, 1, 1), (1, 3, 1), (0, 3, 1),
    ]
    faces = [
        (1,2,3),(1,3,4),(1,4,6),(4,5,6),
        (7,8,9),(7,9,10),(7,10,12),(10,11,12),
        (1,2,8),(1,8,7),(2,3,9),(2,9,8),
        (3,4,10),(3,10,9),(4,5,11),(4,11,10),
        (5,6,12),(5,12,11),(6,1,7),(6,7,12),
        (1,1,2),
    ]
    lines = [f"v {x} {y} {z}" for x, y, z in vertices] + [f"f {a} {b} {c}" for a, b, c in faces]
    path.write_text("\n".join(lines) + "\n")


def write_wave_panel(path: Path, n: int = 24) -> None:
    vertices = []
    faces = []
    for iy in range(n + 1):
        for ix in range(n + 1):
            x = ix / n * 4
            y = iy / n * 4
            z = 0.25 * math.sin(ix / n * math.pi) * math.cos(iy / n * math.pi) + 0.6
            vertices.append((x, y, z))

    def vid(ix: int, iy: int) -> int:
        return iy * (n + 1) + ix + 1

    for iy in range(n):
        for ix in range(n):
            a = vid(ix, iy)
            b = vid(ix + 1, iy)
            c = vid(ix + 1, iy + 1)
            d = vid(ix, iy + 1)
            faces.append((a, b, c))
            faces.append((a, c, d))
    lines = [f"v {x} {y} {z}" for x, y, z in vertices] + [f"f {a} {b} {c}" for a, b, c in faces]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    base = Path("data/input")
    base.mkdir(parents=True, exist_ok=True)
    write_cube(base / "sample_cube.obj")
    write_bracket(base / "sample_bracket.obj")
    write_wave_panel(base / "sample_wave_panel.obj")
    print("Sample geometry written to data/input")


if __name__ == "__main__":
    main()
