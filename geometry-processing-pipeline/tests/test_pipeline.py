import json
from pathlib import Path

from geometry_pipeline.io import load_mesh
from geometry_pipeline.pipeline import process_mesh
from geometry_pipeline.cleanup import repair_mesh


def test_repair_removes_degenerate_faces():
    mesh = load_mesh('data/input/sample_cube.obj')
    repaired = repair_mesh(mesh)
    assert repaired.face_count < mesh.face_count
    assert repaired.vertex_count <= mesh.vertex_count


def test_pipeline_produces_slices():
    mesh = load_mesh('data/input/sample_cube.obj')
    result = process_mesh(mesh, voxel_size=0.25, layer_height=0.2)
    assert len(result.slices) > 0
    assert any(layer['segments'] for layer in result.slices)


def test_simplification_keeps_valid_faces():
    mesh = load_mesh('data/input/sample_bracket.obj')
    result = process_mesh(mesh, voxel_size=0.3, layer_height=0.2)
    for face in result.simplified.faces:
        assert len(set(map(int, face))) == 3
