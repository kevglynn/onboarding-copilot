"""Tests for the scaffold command."""

import ast
import shutil
import subprocess

import pytest

from ob.commands.scaffold import _infer_module_name, _slugify, scaffold_workspace
from ob.guardrails import extract_target_directory
from ob.profile import load_profile


@pytest.fixture
def profile(scikit_image_profile_path):
    return load_profile(scikit_image_profile_path)


class TestScaffoldWorkspace:
    """Tests for workspace scaffolding."""

    def test_creates_workspace_directory(self, tmp_path, profile):
        """Scaffold creates a workspace directory."""
        ws = scaffold_workspace(
            "add adaptive histogram equalization helper",
            profile,
            base_dir=tmp_path,
        )
        assert ws is not None
        assert ws.is_dir()

    def test_creates_plan_md(self, tmp_path, profile):
        """Scaffold creates a PLAN.md file."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        assert (ws / "PLAN.md").exists()

    def test_creates_source_stub(self, tmp_path, profile):
        """Scaffold creates a source file stub."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        py_files = list(ws.rglob("*.py"))
        source_files = [f for f in py_files if not f.name.startswith("test_")]
        assert len(source_files) > 0

    def test_creates_test_stub(self, tmp_path, profile):
        """Scaffold creates a test file stub."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        test_files = list(ws.rglob("test_*.py"))
        assert len(test_files) > 0

    def test_creates_briefs_stub(self, tmp_path, profile):
        """Scaffold creates a BRIEFS.md file."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        assert (ws / "BRIEFS.md").exists()

    def test_plan_references_conventions(self, tmp_path, profile):
        """PLAN.md references the profile's conventions."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        plan = (ws / "PLAN.md").read_text()
        assert "numpydoc" in plan
        assert "snake_case" in plan

    def test_source_has_numpydoc_template(self, tmp_path, profile):
        """Source stub uses numpydoc style for scikit-image profile."""
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        py_files = list(ws.rglob("*.py"))
        source_files = [f for f in py_files if not f.name.startswith("test_")]
        content = source_files[0].read_text()
        assert "Parameters" in content
        assert "Returns" in content


class TestScaffoldGuardrails:
    """Tests for boundary enforcement."""

    def test_refuses_forbidden_path(self, tmp_path, profile):
        """Scaffold refuses to create in forbidden directories."""
        ws = scaffold_workspace(
            "add helper to skimage/_vendored/",
            profile,
            base_dir=tmp_path,
        )
        assert ws is None

    def test_refuses_shared_path(self, tmp_path, profile):
        """Scaffold refuses to create in _shared directory."""
        ws = scaffold_workspace(
            "add to _shared utils",
            profile,
            base_dir=tmp_path,
        )
        assert ws is None

    def test_does_not_falsely_refuse_build_word(self, tmp_path, profile):
        """A task mentioning 'build' (substring of _build) is not refused."""
        ws = scaffold_workspace(
            "add a build helper for thresholding",
            profile,
            base_dir=tmp_path,
        )
        assert ws is not None

    def test_does_not_falsely_refuse_shared_word(self, tmp_path, profile):
        """A task mentioning the word 'shared' is not refused (only _shared)."""
        ws = scaffold_workspace(
            "add shared-memory documentation to filters",
            profile,
            base_dir=tmp_path,
        )
        assert ws is not None


class TestScaffoldLintClean:
    """Scaffolded stubs must pass the repo's own lint gate."""

    def test_stubs_pass_ruff_check(self, tmp_path, profile):
        """Freshly scaffolded code passes `ruff check` with zero errors."""
        ruff = shutil.which("ruff")
        if ruff is None:
            pytest.skip("ruff not on PATH")
        ws = scaffold_workspace("add new filter", profile, base_dir=tmp_path)
        result = subprocess.run(
            [ruff, "check", str(ws)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestScaffoldEdgeCases:
    """Degenerate task strings still produce valid output."""

    def test_numeric_task_produces_valid_module(self, tmp_path, profile):
        """A digit-only task yields a syntactically valid source stub."""
        ws = scaffold_workspace("123", profile, base_dir=tmp_path)
        assert ws is not None
        sources = [f for f in ws.rglob("*.py") if not f.name.startswith("test_")]
        assert sources
        ast.parse(sources[0].read_text())

    def test_symbol_only_task_produces_valid_module(self, tmp_path, profile):
        """A task with no word characters still yields a valid module."""
        ws = scaffold_workspace("!!!", profile, base_dir=tmp_path)
        assert ws is not None
        sources = [f for f in ws.rglob("*.py") if not f.name.startswith("test_")]
        assert sources
        ast.parse(sources[0].read_text())


class TestDirectoryInference:
    """Task descriptions route to the correct approved directory."""

    @pytest.mark.parametrize(
        "task,expected",
        [
            ("add adaptive histogram equalization helper", "skimage/exposure/"),
            ("edge detection filter", "skimage/filters/"),
            ("image denoising", "skimage/restoration/"),
            ("watershed segmentation", "skimage/segmentation/"),
            ("morphological erosion operation", "skimage/morphology/"),
            ("convert rgb to grayscale", "skimage/color/"),
        ],
    )
    def test_keyword_routing(self, profile, task, expected):
        """Keyword hints route tasks to the right module."""
        assert extract_target_directory(task, profile) == expected

    def test_io_not_matched_inside_equalization(self, profile):
        """Regression: 'io' must not match as a substring of 'equalization'."""
        result = extract_target_directory(
            "add adaptive histogram equalization helper", profile
        )
        assert result == "skimage/exposure/"
        assert result != "skimage/io/"

    def test_explicit_module_name_matches_as_whole_word(self, profile):
        """A real module name as a whole word still routes correctly."""
        assert extract_target_directory("add a new io reader", profile) == "skimage/io/"

    def test_unmatched_task_returns_none(self, profile):
        """No keyword/module match returns None (caller uses default)."""
        assert extract_target_directory("a totally unrelated request", profile) is None

    def test_scaffold_routes_equalization_to_exposure(self, tmp_path, profile):
        """End-to-end: scaffold places equalization files under exposure, not io."""
        ws = scaffold_workspace(
            "add adaptive histogram equalization helper",
            profile,
            base_dir=tmp_path,
        )
        assert ws is not None
        exposure_files = list((ws / "skimage" / "exposure").rglob("*.py"))
        assert exposure_files, "expected source under skimage/exposure/"
        assert not (ws / "skimage" / "io").exists()


class TestScaffoldHonorsProfileLayout:
    """Scaffold derives test location and names from the profile (xm1.4)."""

    def test_skimage_test_colocated_and_named_from_patterns(self, tmp_path, profile):
        """scikit-image: tests co-located, methods from required_patterns."""
        ws = scaffold_workspace("edge detection filter", profile, base_dir=tmp_path)
        test_files = list(ws.rglob("test_*.py"))
        assert test_files
        rel = test_files[0].relative_to(ws).as_posix()
        assert rel.startswith("skimage/filters/tests/"), rel
        content = test_files[0].read_text()
        assert "def test_shape_preservation" in content
        assert "def test_dtype_roundtrip" in content

    def test_diffusers_layout_and_google_docstring(
        self, tmp_path, diffusers_profile_path
    ):
        """diffusers: tests under tests/, google docstring, profile test names."""
        profile = load_profile(diffusers_profile_path)
        ws = scaffold_workspace("add a new scheduler", profile, base_dir=tmp_path)
        sources = [f for f in ws.rglob("*.py") if not f.name.startswith("test_")]
        assert any("Args:" in f.read_text() for f in sources)
        test_files = list(ws.rglob("test_*.py"))
        assert test_files
        rel = test_files[0].relative_to(ws).as_posix()
        assert rel.startswith("tests/"), rel
        content = test_files[0].read_text()
        assert "def test_output_shape" in content
        assert "def test_deterministic_seed" in content


class TestSlugify:
    """Tests for the slugify helper."""

    def test_basic_slugify(self):
        assert _slugify("Add New Filter") == "add-new-filter"

    def test_special_characters(self):
        assert _slugify("add (new) filter!") == "add-new-filter"

    def test_truncation(self):
        long_text = "a" * 100
        assert len(_slugify(long_text)) <= 60


class TestInferModuleName:
    """Tests for module name inference."""

    def test_basic_name(self):
        assert _infer_module_name("add new filter") == "add_new_filter"

    def test_hyphen_to_underscore(self):
        name = _infer_module_name("add-new-filter")
        assert "_" in name or "-" not in name
