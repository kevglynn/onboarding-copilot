# Contribution Plan: Add Adaptive Histogram Equalization Helper

Per SK-D-001 (approved directories), new filter helpers go in `skimage/filters/`.
Per SK-T-001 (testing conventions), tests go in `skimage/filters/tests/test_<module>.py`
with at least one shape-preservation case and one dtype-roundtrip case.

## Task
Add an adaptive histogram equalization convenience wrapper to `skimage.filters`.

## Files to Create/Modify
- `skimage/filters/_adaptive_equalize.py` — implementation
- `skimage/filters/tests/test_adaptive_equalize.py` — tests

## Design Notes
- Wraps `skimage.exposure.equalize_adapthist` with filter-module conventions
- Accepts 2D grayscale images as `(M, N) ndarray`
- `clip_limit` parameter controls contrast limiting (default 0.01)
- `kernel_size` parameter controls local region size (default None → 1/8 of image)
- Returns float64 image in [0, 1] range per exposure module convention
- Validates input dimensions and raises `ValueError` for non-2D input

## Conventions Applied
- SK-D-001: File placed in `skimage/filters/` (approved directory)
- SK-N-001: Function uses `snake_case` naming
- SK-DOC-001: NumPy-style docstring with Parameters, Returns, Examples, References
- SK-T-001: Tests cover shape preservation, dtype roundtrip, edge cases
- SK-T-002: Test file named `test_adaptive_equalize.py` in `skimage/filters/tests/`
