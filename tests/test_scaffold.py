"""Tests for the scaffold command."""

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
