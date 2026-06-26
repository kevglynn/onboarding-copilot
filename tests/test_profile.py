"""Tests for profile loading and validation."""

import pytest
import yaml
from pydantic import ValidationError

from ob.profile import load_profile


class TestLoadProfile:
    """Tests for the load_profile function."""

    def test_loads_scikit_image_profile(self, scikit_image_profile_path):
        """scikit-image profile loads and validates without error."""
        profile = load_profile(scikit_image_profile_path)
        assert profile.name == "scikit-image"

    def test_loads_diffusers_profile(self, diffusers_profile_path):
        """Diffusers stub profile loads and validates without error."""
        profile = load_profile(diffusers_profile_path)
        assert profile.name == "diffusers"

    def test_profile_not_found_raises(self, tmp_path):
        """Raises FileNotFoundError for missing profile."""
        with pytest.raises(FileNotFoundError, match="Profile not found"):
            load_profile(tmp_path / "nonexistent.yaml")

    def test_invalid_yaml_raises_validation_error(self, tmp_path):
        """Raises ValidationError for YAML that doesn't match schema."""
        bad_profile = tmp_path / "bad.yaml"
        bad_profile.write_text("name: test\n")
        with pytest.raises(ValidationError):
            load_profile(bad_profile)


class TestScikitImageProfile:
    """Tests for scikit-image profile content."""

    def test_has_approved_directories(self, scikit_image_profile_path):
        """Profile defines approved directories."""
        profile = load_profile(scikit_image_profile_path)
        assert len(profile.approved_directories) > 0
        assert "skimage/filters/" in profile.approved_directories

    def test_has_forbidden_paths(self, scikit_image_profile_path):
        """Profile defines forbidden paths."""
        profile = load_profile(scikit_image_profile_path)
        assert len(profile.forbidden_paths) > 0
        assert "skimage/_shared/" in profile.forbidden_paths

    def test_has_deprecated_apis(self, scikit_image_profile_path):
        """Profile lists deprecated APIs with replacements."""
        profile = load_profile(scikit_image_profile_path)
        assert len(profile.deprecated_apis) > 0
        symbols = [api.symbol for api in profile.deprecated_apis]
        assert "skimage.filters.median" in symbols

    def test_has_test_conventions(self, scikit_image_profile_path):
        """Profile specifies test conventions."""
        profile = load_profile(scikit_image_profile_path)
        assert profile.test_conventions.framework == "pytest"
        assert profile.test_conventions.file_pattern == "test_*.py"

    def test_has_docstring_convention(self, scikit_image_profile_path):
        """Profile specifies numpydoc docstring style."""
        profile = load_profile(scikit_image_profile_path)
        assert profile.docstring_convention.style == "numpydoc"
        assert profile.docstring_convention.array_shape_notation is True

    def test_has_role_brief_templates(self, scikit_image_profile_path):
        """Profile defines brief templates for all four roles."""
        profile = load_profile(scikit_image_profile_path)
        roles = {t.role for t in profile.role_brief_templates}
        assert roles == {"engineer", "pm", "qa", "devops"}

    def test_naming_convention(self, scikit_image_profile_path):
        """Profile specifies snake_case naming convention."""
        profile = load_profile(scikit_image_profile_path)
        assert profile.naming_convention == "snake_case"


class TestProfileSchema:
    """Tests for schema enforcement."""

    def test_missing_approved_directories_fails(self, tmp_path):
        """Profile without approved_directories fails validation."""
        data = {
            "name": "test",
            "version": "0.1.0",
            "description": "test",
            "forbidden_paths": [],
            "test_conventions": {
                "framework": "pytest",
                "file_pattern": "test_*.py",
                "location_pattern": "tests/",
            },
            "docstring_convention": {"style": "google"},
        }
        profile_path = tmp_path / "test.yaml"
        profile_path.write_text(yaml.dump(data))
        with pytest.raises(ValidationError, match="approved_directories"):
            load_profile(profile_path)

    def test_missing_forbidden_paths_fails(self, tmp_path):
        """Profile without forbidden_paths fails validation."""
        data = {
            "name": "test",
            "version": "0.1.0",
            "description": "test",
            "approved_directories": ["src/"],
            "test_conventions": {
                "framework": "pytest",
                "file_pattern": "test_*.py",
                "location_pattern": "tests/",
            },
            "docstring_convention": {"style": "google"},
        }
        profile_path = tmp_path / "test.yaml"
        profile_path.write_text(yaml.dump(data))
        with pytest.raises(ValidationError, match="forbidden_paths"):
            load_profile(profile_path)
