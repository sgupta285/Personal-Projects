from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from .mesh import Mesh


def _add_mesh(ax, mesh: Mesh, color: str = "steelblue") -> None:
    tri = mesh.face_vertices()
    collection = Poly3DCollection(tri, alpha=0.55, linewidths=0.2)
    collection.set_facecolor(color)
    collection.set_edgecolor("black")
    ax.add_collection3d(collection)
    mins, maxs = mesh.bounds()
    ax.set_xlim(mins[0], maxs[0])
    ax.set_ylim(mins[1], maxs[1])
    ax.set_zlim(mins[2], maxs[2])


def save_mesh_comparison(original: Mesh, processed: Mesh, path: str | Path, title_left: str = "Original", title_right: str = "Processed") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(10, 4))
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    _add_mesh(ax1, original, color="steelblue")
    _add_mesh(ax2, processed, color="darkorange")
    ax1.set_title(title_left)
    ax2.set_title(title_right)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_slice_preview(slices: list[dict], path: str | Path, max_layers: int = 6) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    plotted = 0
    for layer in slices:
        if plotted >= max_layers:
            break
        segments = layer["segments"]
        if not segments:
            continue
        for seg in segments:
            xs = [seg[0][0], seg[1][0]]
            ys = [seg[0][1], seg[1][1]]
            ax.plot(xs, ys, linewidth=1)
        plotted += 1
    ax.set_title("Slice segment preview")
    ax.set_aspect('equal', 'box')
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_benchmark_chart(rows: list[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = [row["name"] for row in rows]
    totals = [row["total_seconds"] for row in rows]
    peaks = [row["peak_memory_mb"] for row in rows]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(names, totals)
    axes[0].set_title("Runtime by mesh")
    axes[0].set_ylabel("seconds")
    axes[1].bar(names, peaks)
    axes[1].set_title("Peak memory by mesh")
    axes[1].set_ylabel("MB")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
