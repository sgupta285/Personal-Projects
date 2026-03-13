# Edge Cases and Failure Modes

## Edge cases covered by tests

- duplicate vertices map back into a compact vertex array
- degenerate faces are removed during repair
- slicing a closed cube returns valid non-empty slice layers
- simplification does not leave faces with repeated vertex indices

## Known limitations

- no binary STL parser
- no true hole filling or manifold healing
- smoothing is uniform Laplacian, so boundary-aware constraints are not included
- slicing exports raw segments, not stitched contours
