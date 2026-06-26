# Role Briefs: Adaptive Histogram Equalization Helper

## Engineer Brief

### Implementation Checklist
- [x] Source file: `skimage/filters/_adaptive_equalize.py`
- [x] Test file: `skimage/filters/tests/test_adaptive_equalize.py`
- [x] NumPy-style docstring with Parameters, Returns, Examples, References
- [x] Input validation (2D check, clip_limit range)
- [x] Snake_case function name per SK-N-001
- [ ] Gallery example (deferred — not required for internal helper)

### File Map
```
skimage/filters/
├── _adaptive_equalize.py    ← new file (implementation)
└── tests/
    └── test_adaptive_equalize.py  ← new file (9 tests)
```

### Convention Reminders
- Array params documented with shape notation: `(M, N) ndarray`
- Build with `spin build`, test with `spin test`
- Strict warnings enabled — `SKIMAGE_TEST_STRICT_WARNINGS=1`

---

## PM Brief

### Scope
Small, self-contained helper that wraps existing CLAHE functionality in the
`skimage.filters` module. No new dependencies. No API surface changes to
existing code.

### User Impact
Engineers working with low-contrast images get a convenience function
in the filters module where they'd naturally look for it, instead of
discovering `skimage.exposure.equalize_adapthist` by reading docs.

### What to Ask in Kickoff
- Is this discoverable enough without a gallery example?
- Should this be `skimage.filters.adaptive_equalize` (public) or stay private?
- Any existing issues requesting this?

---

## QA Brief

### Test Strategy
9 tests covering:
- Shape preservation (output shape == input shape)
- Dtype contract (always returns float64)
- Output range enforcement ([0, 1])
- Edge case: uniform image
- Input validation: 3D, 1D, out-of-range clip_limit
- Custom kernel_size acceptance
- uint8 input handling

### Edge Cases to Watch
- Very small images (< kernel_size)
- Images with NaN or Inf values (not yet handled)
- Large images (memory pressure from CLAHE tiling)

### Test Names We Will Reject
- `test_it_works` — not descriptive
- `test_result` — doesn't specify what about the result
- `test_adaptive_equalize` — just restates the function name

---

## DevOps Brief

### CI Guardrails
- `ob check` validates: test file exists, no TODO-only implementations,
  no forbidden imports, file in approved directory
- `ruff check` enforces style
- `pytest` runs all 9 tests

### Pipeline Signal
- All checks pass → safe to merge
- `ob check` failure → convention violation, block merge
- `pytest` failure → functional regression, block merge

### Boundary Enforcement
- Source file in `skimage/filters/` (approved directory ✓)
- No imports from `skimage._shared` private modules ✓
- No deprecated API usage ✓
