"""Tests for the scaffold command."""

import pytest

from ob.commands.scaffold import _infer_module_name, _slugify, scaffold_workspace
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
