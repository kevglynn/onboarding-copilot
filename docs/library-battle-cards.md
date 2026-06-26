# Library Battle Cards: scikit-image vs OpenCV

Prepared for an "Engineering Onboarding Copilot" interview where the candidate chose scikit-image over OpenCV and needs to defend that choice.

---

## scikit-image

### 1. Identity

| Field | Details |
|-------|---------|
| What it is | A pure-Python image processing library built on NumPy arrays, part of the scientific Python (SciPy) ecosystem |
| Primary language | Python (with some Cython for performance-critical paths) |
| GitHub stats | ~6,500 stars / ~600 contributors |
| License | BSD-3-Clause (some vendored code is BSD-2-Clause) |
| Maintainers | Community-governed under the scientific Python umbrella; core team includes Stéfan van der Walt, Lars Grüter, Juan Nunez-Iglesias, Jarrod Millman, Marianne Corvellec, Matthew Brett |

### 2. Architecture & Conventions

**Codebase organization:**
```
scikit-image/
├── skimage/              # Main package (being migrated to _skimage2 for v2.0)
│   ├── color/            # Color space conversions
│   ├── data/             # Built-in example images
│   ├── draw/             # Drawing primitives
│   ├── exposure/         # Histogram equalization, contrast
│   ├── feature/          # Corner detection, texture, blobs
│   ├── filters/          # Edge detection, thresholding, rank filters
│   ├── graph/            # Graph-based operations
│   ├── io/               # Image I/O
│   ├── measure/          # Region properties, contours
│   ├── metrics/          # Distance, similarity metrics
│   ├── morphology/       # Erosion, dilation, skeletonization
│   ├── registration/     # Optical flow, phase correlation
│   ├── restoration/      # Denoising, deconvolution
│   ├── segmentation/     # Watershed, SLIC, random walker
│   ├── transform/        # Geometric transforms, Radon
│   └── util/             # Generic utilities
├── doc/                  # Sphinx + Sphinx-Gallery documentation
├── benchmarks/           # ASV performance benchmarks
├── requirements/         # Dependency files (build.txt, test.txt, etc.)
├── tools/                # Development scripts
├── meson.build           # Build system (Meson, not setuptools)
└── pyproject.toml        # PEP 517 metadata
```

**Naming conventions:**
- Functions: `snake_case` (e.g., `threshold_otsu`, `label2rgb`, `binary_dilation`)
- Modules: `snake_case`, thematic grouping (e.g., `skimage.filters`, `skimage.morphology`)
- Tests: `test_<function_name>.py` or `test_<topic>.py` inside `skimage/<module>/tests/`
- Import convention: `import skimage as ski` then `ski.filters.gaussian()`

**Testing framework:**
- pytest with `pytest-cov`, `pytest-localserver`, `pytest-faulthandler`
- Tests live in `skimage/<submodule>/tests/` directories
- Run via `spin test` (the `spin` developer tool wraps Meson build + pytest)
- Doctests also enforced: `spin test -- --doctest-plus skimage`
- Strict warnings: `SKIMAGE_TEST_STRICT_WARNINGS=1` by default; warnings are errors
- Target: 100% statement coverage per module

**Documentation conventions:**
- NumPy-style docstrings (numpydoc standard)
- Array params documented with shape: `image : (M, N) ndarray`
- Every public function must have a docstring with Parameters, Returns, Examples sections
- Gallery examples built with Sphinx-Gallery (max figure width 8 inches)
- New features require a gallery example

**CI/CD:**
- GitHub Actions (fully migrated from Azure Pipelines as of early 2025)
- Matrix builds: Linux (Python 3.12, 3.13, 3.14, 3.14t), Windows
- Uses `spin build` then `spin test --doctest`
- Wheel building and PyPI release via separate workflow (`wheels-test-and-release.yaml`)
- ccache for build caching
- Label `run-all-tests` to override the default "test only modified" behavior on PRs

**Contribution workflow:**
1. Fork → clone → create feature branch (e.g., `transform-speedups`)
2. Use pre-commit hooks (code formatters, PEP8 checkers)
3. Build with `spin build`, test with `spin test`
4. Submit PR → CI runs automatically (build, test, coverage, style)
5. **Two core team approvals required** before merge
6. Review culture is explicitly mentorship-oriented; reviewers fix nitpicks themselves

### 3. Onboarding Complexity

**Difficulty level:** Moderate — accessible for Python developers, but the build system (Meson + Cython compilation) can trip people up.

**Common new-contributor mistakes:**
- Running `pytest` directly in the repo root instead of using `spin test` (causes import errors because Cython extensions aren't compiled)
- Not realizing that pushing to their branch auto-updates the PR
- Forgetting to add a gallery example for new functionality
- Submitting code without docstrings or with wrong docstring format (numpydoc is strict)
- Not running with strict warnings enabled, then failing CI

**Non-obvious conventions:**
- The `spin` tool is mandatory — you cannot just `pip install -e .` and `pytest` anymore (Meson build system)
- Array parameters must be documented with dimension letters: `(M, N)` not just `ndarray`
- Gallery examples are mandatory for new features, not optional
- The project is mid-migration to `skimage2` namespace — new code may land in `_skimage2/`
- Images are always NumPy arrays (not custom Image objects) — this is a core design philosophy

**Gotchas:**
- Build requires a C compiler (for Cython extensions) even though it's "a Python library"
- The `future` submodule has experimental APIs that may change
- `SKIMAGE_TEST_STRICT_WARNINGS=1` means upstream dependency deprecation warnings will fail your tests

### 4. Why Choose This Library (for the Copilot Demo)

**Strengths as a demo target:**
- Pure Python + NumPy idioms — the copilot can reason about code at a high level without C++ complexity
- Extremely consistent conventions (numpydoc, snake_case everywhere, predictable module layout)
- Rich documentation with gallery examples = lots of training signal for a copilot
- Welcoming contributor culture with explicit mentorship norms
- Moderate codebase size (~600 contributors, not overwhelming like OpenCV's 2000+)
- Clean separation of concerns (each submodule is self-contained)

**Weaknesses as a demo target:**
- Smaller community than OpenCV = less variety in contribution patterns
- Currently in a major refactoring (skimage → skimage2) which adds confusion
- The Meson build system is less commonly understood than CMake or setuptools
- Fewer "gotchas" to catch = potentially less dramatic demo of copilot value

### 5. Talking Points

**Things to say fluently:**
1. "scikit-image represents images as plain NumPy arrays — no custom Image class. This makes it composable with the entire scientific Python stack (SciPy, matplotlib, pandas) without conversion layers."
2. "The library enforces numpydoc-format docstrings with mandatory Examples sections and Sphinx-Gallery examples for all new features. This documentation discipline gives a copilot rich, structured context to learn from."
3. "PRs require two core team approvals and the review culture is explicitly mentorship-focused — reviewers fix typos themselves rather than asking contributors to. This creates very clean, consistent commit history."
4. "The codebase uses the `spin` developer tool to wrap Meson builds and pytest execution, which standardizes the development workflow across all contributors."

**Watch out for:**
1. *"Isn't scikit-image just a wrapper around OpenCV?"* — No. It's an independent implementation with different design philosophy (readability over raw performance, NumPy-native, pure-Python-first).
2. *"How does scikit-image handle video or real-time processing?"* — It doesn't, really. It's frame-by-frame image processing. Real-time pipelines are OpenCV's territory. Know this gap.
3. *"Why not just use OpenCV's Python bindings?"* — The bindings are auto-generated from C++ and don't follow Python conventions (camelCase, opaque Mat objects vs. transparent NumPy arrays, inconsistent error messages).

---

## OpenCV

### 1. Identity

| Field | Details |
|-------|---------|
| What it is | The world's most widely-adopted computer vision library, providing 2,500+ optimized algorithms for image processing, video analysis, object detection, and DNN inference |
| Primary language | C++ (with auto-generated bindings for Python, Java, JavaScript, Objective-C, Swift) |
| GitHub stats | ~88,700 stars / ~2,185 total committers (280 shown on GitHub UI) |
| License | Apache License 2.0 |
| Maintainers | OpenCV.org (Open Source Vision Foundation, a US 501(c)(3) non-profit); Intel is a Platinum Member; stewarded by Big Vision, OpenCV China, and OpenCV.ai. Founded by Gary Bradski |

### 2. Architecture & Conventions

**Codebase organization:**
```
opencv/
├── modules/              # Core library modules (each is self-contained)
│   ├── core/             # Basic data structures, math, utilities
│   ├── imgproc/          # Image processing (filtering, geometric transforms)
│   ├── imgcodecs/        # Image file reading/writing
│   ├── videoio/          # Video capture and writing
│   ├── video/            # Motion analysis, object tracking
│   ├── highgui/          # GUI windows, trackbars
│   ├── calib3d/          # Camera calibration, stereo vision
│   ├── features2d/       # Feature detection (ORB, AKAZE, etc.)
│   ├── objdetect/        # Object detection (Haar cascades, QR codes)
│   ├── dnn/              # Deep neural network inference (ONNX, TensorFlow)
│   ├── flann/            # Fast approximate nearest neighbor
│   ├── ml/               # Machine learning (SVM, Random Forest, etc.)
│   ├── photo/            # Computational photography
│   ├── stitching/        # Image stitching
│   ├── gapi/             # Graph-based image processing pipeline API
│   ├── python/           # Python binding generator
│   ├── java/             # Java binding generator
│   ├── js/               # JavaScript (WebAssembly) bindings
│   └── ts/               # Test framework (bundled Google Test)
├── cmake/                # CMake build infrastructure
├── doc/                  # Doxygen documentation + tutorials
├── samples/              # Example programs (C++, Python, Java)
├── data/                 # Haar cascades, test data
├── platforms/            # Platform-specific build scripts (iOS, Android, etc.)
├── 3rdparty/             # Vendored third-party libraries
└── apps/                 # Standalone applications
```

Each module follows:
```
modules/<name>/
├── CMakeLists.txt        # Module declaration via ocv_define_module()
├── include/opencv2/      # Public headers (*.hpp)
├── src/                  # Implementation (*.cpp)
├── test/                 # Accuracy/regression tests
└── perf/                 # Performance tests
```

**Naming conventions:**
- Functions/methods: `camelCase` starting lowercase (e.g., `cv::cvtColor`, `cv::GaussianBlur`)
- Exception: algorithms named after authors start uppercase (e.g., `cv::Sobel`, `cv::Canny`)
- Classes: `PascalCase` (e.g., `cv::Mat`, `cv::VideoCapture`)
- Macros/enums: `ALL_CAPS_WITH_UNDERSCORES` (e.g., `CV_EXPORTS`, `COLOR_BGR2GRAY`)
- Public API marked with `CV_EXPORTS` macro; `CV_EXPORTS_W` for Python/Java binding exposure
- Python bindings: auto-generated, preserving C++ camelCase (e.g., `cv2.cvtColor()`)

**Testing framework:**
- Google Test (bundled in `modules/ts/`), not an external dependency
- Accuracy tests: `modules/<name>/test/` → binary `opencv_test_<module>`
- Performance tests: `modules/<name>/perf/` → binary `opencv_perf_<module>`
- Test naming: `TEST(ModuleName_FunctionOrClass, TestType) { ... }`
- All test code in `opencv_test` namespace
- Test data stored in separate repo: `opencv/opencv_extra` (requires `OPENCV_TEST_DATA_PATH` env var)
- Files must include `test_precomp.hpp` first

**Documentation conventions:**
- Doxygen comments in headers (`/** ... */`)
- Tutorials are separate markdown/RST files in `doc/tutorials/`
- Python API docs are auto-generated from C++ annotations
- `@param`, `@return`, `@note`, `@code` Doxygen tags

**CI/CD:**
- GitHub Actions + custom OpenCV buildbot (pullrequest.opencv.org)
- Tests run on Linux, Windows, macOS, Android
- Multi-architecture: x86, ARM, RISC-V
- Two-stage: GitHub Actions for quick checks, buildbot for full platform matrix

**Contribution workflow:**
1. Fork → create branch (avoid naming it same as upstream branches)
2. Target the right branch: bug fixes/small features → `4.x`, large features → `5.x`
3. Fill out PR readiness checklist (Apache 2.0 agreement, proper branch, tests, docs)
4. CI runs automatically (GitHub Actions + buildbot)
5. One reviewer approval (signaled by 👍 emoji) → maintainer merges
6. New algorithms must go to `opencv_contrib` repository first
7. Coordinate via issues before submitting — "out of the blue" PRs often get rejected

### 3. Onboarding Complexity

**Difficulty level:** High — the C++ build system (CMake), massive codebase, multi-language binding generation, and corporate review process create significant barriers.

**Common new-contributor mistakes:**
- Submitting PRs without a linked issue ("out of the blue" PRs are regularly rejected)
- Targeting the wrong branch (e.g., sending a large feature to `4.x` instead of `5.x`)
- Not squashing "oops" fixup commits before submitting
- Being confused by the CMake module system and the `ocv_define_module` macro
- Forgetting to set `OPENCV_TEST_DATA_PATH` to run tests locally
- Including GPL-licensed code (incompatible with Apache 2.0)
- Not adding performance tests for optimization PRs

**Non-obvious conventions:**
- Test data lives in a completely separate repository (`opencv_extra`)
- Python bindings are auto-generated from C++ header annotations (`CV_EXPORTS_W`, `CV_WRAP`) — you never write Python binding code directly
- The `master` branch is a shadow copy of `4.x`; the `next` branch is a shadow copy of `5.x` — never target these directly
- You must respond to reviewers within weeks or your PR may be rejected
- Patent checks are expected for new algorithm implementations
- Performance tests are not optional for optimization PRs

**Gotchas:**
- Building from source can take 30+ minutes; requires CMake, C++ compiler, and optionally CUDA, FFmpeg, etc.
- The Python `cv2` module is monolithic — you can't `import cv2.imgproc`, just `import cv2`
- Error messages from Python bindings are often cryptic (C++ exceptions translated poorly)
- OpenCV uses BGR color order by default, not RGB — a constant source of bugs

### 4. Why Choose This Library (for the Copilot Demo)

**Strengths as a demo target:**
- Massive user base = huge surface area for onboarding pain points
- Complex build system and multi-language architecture create real onboarding friction
- Non-obvious conventions (BGR, `CV_EXPORTS_W` annotations, separate test data repo) are exactly what a copilot could help with
- Extremely diverse contribution types (C++, Python bindings, CUDA kernels, ONNX models)

**Weaknesses as a demo target:**
- The C++ codebase is hard to parse and reason about programmatically
- Auto-generated Python bindings mean the "Python API" isn't really Python — limited conventional patterns for an LLM to learn
- Build complexity makes local testing and iteration slow for demo purposes
- Corporate governance makes the contribution process harder to demonstrate in a controlled environment
- Much of the relevant convention knowledge is in wiki pages, not in-repo (harder to index)

### 5. Talking Points

**Things to say fluently:**
1. "OpenCV is a C++ library with auto-generated polyglot bindings. The Python API you see as `cv2.cvtColor()` is generated from `CV_EXPORTS_W` annotations in C++ headers — there's no hand-written Python layer."
2. "The project has a two-repo model: `opencv/opencv` for stable modules and `opencv/opencv_contrib` for experimental algorithms. New algorithm implementations are required to start in contrib before promotion to the main repo."
3. "Test data lives in a separate repository (`opencv_extra`) that you must clone and set via environment variable. This is a frequent gotcha that blocks new contributors from running tests locally."
4. "OpenCV 5.0 (released June 2026) introduced a graph-based DNN engine with broad ONNX coverage — it's increasingly a DNN inference framework, not just classical CV."

**Watch out for:**
1. *"If OpenCV has Python bindings, why not just use those?"* — The bindings don't follow Python conventions (camelCase, no type hints, opaque `Mat` objects, cryptic errors). scikit-image gives you idiomatic Python with NumPy arrays.
2. *"Doesn't OpenCV have more algorithms?"* — Yes, significantly more (~2,500 vs ~hundreds). But for an onboarding copilot demo, what matters is contribution pattern consistency, not algorithm breadth. scikit-image's uniform conventions are easier to learn from.
3. *"How would a copilot help with OpenCV's C++ code?"* — It could help with the binding annotations (`CV_EXPORTS_W`, `CV_WRAP`, `CV_OUT`), CMake module declarations, and the non-obvious test infrastructure. But the complexity of C++ template metaprogramming in OpenCV's core makes reliable code generation much harder.

---

## Summary: Why scikit-image over OpenCV for the Copilot Demo

| Dimension | scikit-image | OpenCV |
|-----------|-------------|--------|
| Language complexity | Python (readable, predictable) | C++ with generated bindings (opaque) |
| Convention consistency | Extremely consistent (numpydoc, snake_case, spin workflow) | Mixed (C++ style + auto-gen Python + wiki-based docs) |
| Onboarding friction | Moderate (build system, gallery requirement) | High (CMake, cross-repo test data, patent checks) |
| Documentation quality | Structured, in-repo, machine-parseable | Scattered (Doxygen + wiki + tutorials + samples) |
| Contributor base size | ~600 (manageable, learnable patterns) | ~2,185 (chaotic variety) |
| Review culture | Mentorship-first, two approvals, fix nitpicks for contributor | Corporate, one approval, respond-or-get-rejected |
| Demo value for copilot | High: uniform conventions make "learn from codebase" tractable | High friction but harder to demonstrate value convincingly |

**The core argument:** scikit-image's deliberately uniform conventions, mandatory documentation standards, and Python-native design make it an ideal target for demonstrating that a copilot can learn a project's norms and guide new contributors. OpenCV's value as a demo target would be showing the copilot handling complexity — but complexity also makes it harder to build a convincing, reliable demo.
