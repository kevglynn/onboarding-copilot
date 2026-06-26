# Contribution Plan: Add Local Contrast Normalization Helper

## Task
Add a local contrast normalization function to `skimage.filters`.

## Files to Create/Modify
- `skimage/filters/_local_contrast.py` — implementation
- `skimage/filters/tests/test_local_contrast.py` — tests

## Design Notes
- Should accept 2D grayscale images
- Window size parameter for local neighborhood
- Return normalized image with same dtype as input
