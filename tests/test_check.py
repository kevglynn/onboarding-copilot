"""Tests for the check command."""

import pytest

from ob.commands.check import check_workspace
from ob.profile import load_profile


@pytest.fixture
def profile(scikit_image_profile_path):
    return load_profile(scikit_image_profile_path)


class TestCheckBadContrib:
    """Check command correctly flags seeded violations."""

    def test_bad_contrib_has_violations(self, examples_dir, profile):
        """bad-first-contrib should produce violations."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        assert not result.passed
        assert len(result.violations) >= 4

    def test_detects_missing_test_file(self, examples_dir, profile):
        """Flags missing test file for _local_contrast.py."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert "SK-T-002" in rule_ids

    def test_detects_todo_only_impl(self, examples_dir, profile):
        """Flags TODO-only implementation."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert "SK-I-001" in rule_ids

    def test_detects_forbidden_import(self, examples_dir, profile):
        """Flags import from forbidden _shared module."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert "SK-F-001" in rule_ids

    def test_detects_deprecated_api(self, examples_dir, profile):
        """Flags deprecated skimage.filters.median usage."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert "SK-D-001" in rule_ids

    def test_detects_wrong_docstring_style(self, examples_dir, profile):
        """Flags Google-style docstring in numpydoc project."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert "SK-DOC-001" in rule_ids


class TestCheckGoodContrib:
    """Check command passes clean code."""

    def test_safe_contrib_passes(self, examples_dir, profile):
        """safe-first-contrib should pass all checks."""
        result = check_workspace(examples_dir / "safe-first-contrib", profile)
        assert result.passed, (
            f"Expected clean pass, got: "
            f"{[(v.rule_id, v.message) for v in result.violations]}"
        )


class TestCheckEdgeCases:
    """Edge cases for the checker."""

    def test_empty_workspace(self, tmp_path, profile):
        """Empty workspace passes (nothing to check)."""
        result = check_workspace(tmp_path, profile)
        assert result.passed

    def test_init_only_workspace(self, tmp_path, profile):
        """Workspace with only __init__.py passes."""
        (tmp_path / "__init__.py").write_text("")
        result = check_workspace(tmp_path, profile)
        assert result.passed
