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


class TestRulePrefixIsProfileDriven:
    """Rule-ID namespace comes from the profile, not hardcoded to scikit-image.

    This is what makes the profile swap honest: swapping the YAML renames the
    whole rule catalog (SK-* -> DIFF-*), proving the engine is library-agnostic.
    """

    def test_diffusers_profile_renames_rule_namespace(
        self, examples_dir, diffusers_profile_path
    ):
        """Same workspace, diffusers profile -> DIFF-* rule IDs, never SK-*."""
        profile = load_profile(diffusers_profile_path)
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]

        assert rule_ids, "expected violations under the diffusers profile"
        assert all(rid.startswith("DIFF-") for rid in rule_ids), rule_ids
        assert not any(rid.startswith("SK-") for rid in rule_ids), rule_ids
        # Profile-independent checks (missing test, TODO-only) still fire.
        assert "DIFF-T-002" in rule_ids
        assert "DIFF-I-001" in rule_ids

    def test_default_prefix_is_sk(self, examples_dir, profile):
        """The scikit-image profile keeps the SK-* namespace."""
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        rule_ids = [v.rule_id for v in result.violations]
        assert all(rid.startswith("SK-") for rid in rule_ids), rule_ids


class TestViolationCountsLocked:
    """Demo invariants: exact rule set on the seeded examples.

    These guard the numbers narrated in README/demo.md ("5 violations",
    "2 under diffusers"). Any checker change that shifts them must update the
    narrative deliberately, not silently.
    """

    def test_bad_contrib_count_locked(self, examples_dir, profile):
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        ids = sorted(v.rule_id for v in result.violations)
        assert ids == [
            "SK-D-001",
            "SK-DOC-001",
            "SK-F-001",
            "SK-I-001",
            "SK-T-002",
        ], ids

    def test_diffusers_bad_contrib_count_locked(
        self, examples_dir, diffusers_profile_path
    ):
        profile = load_profile(diffusers_profile_path)
        result = check_workspace(examples_dir / "bad-first-contrib", profile)
        ids = sorted(v.rule_id for v in result.violations)
        assert ids == ["DIFF-I-001", "DIFF-T-002"], ids


class TestCheckerDetectionGaps:
    """Regression tests for under-detection (xm1.2)."""

    def test_detects_plain_forbidden_import(self, tmp_path, profile):
        """`import skimage._shared.utils` (not just `from`) is flagged."""
        (tmp_path / "_x.py").write_text("import skimage._shared.utils\n")
        result = check_workspace(tmp_path, profile)
        assert "SK-F-001" in [v.rule_id for v in result.violations]

    def test_detects_deprecated_attribute_usage(self, tmp_path, profile):
        """Idiomatic `ski.filters.median(...)` attribute usage is flagged."""
        (tmp_path / "_u.py").write_text(
            "import skimage as ski\n\n\ndef use_it(image):\n"
            "    return ski.filters.median(image)\n"
        )
        result = check_workspace(tmp_path, profile)
        assert "SK-D-001" in [v.rule_id for v in result.violations]

    def test_diffusers_forbidden_import_fires_with_src_layout(
        self, tmp_path, diffusers_profile_path
    ):
        """src-layout forbidden import fires despite the `src/` prefix."""
        profile = load_profile(diffusers_profile_path)
        (tmp_path / "_p.py").write_text(
            "from diffusers._internal.helpers import thing\n"
        )
        result = check_workspace(tmp_path, profile)
        assert "DIFF-F-001" in [v.rule_id for v in result.violations]

    def test_missing_test_flagged_for_public_module(self, tmp_path, profile):
        """A PUBLIC source module with no matching test is flagged, not just
        private (underscore-prefixed) modules.

        The documented SK-T-002 rule is 'flag a source module that has no
        matching test file' — with no private-only qualifier. This guards
        against the checker silently ignoring public API files.
        """
        (tmp_path / "rank.py").write_text(
            '"""Public module."""\n\n\ndef sharpen(image):\n    return image\n'
        )
        result = check_workspace(tmp_path, profile)
        assert "SK-T-002" in [v.rule_id for v in result.violations]

    def test_flags_missing_required_docstring_section(self, tmp_path, profile):
        """A numpydoc function missing a required section is flagged."""
        (tmp_path / "_m.py").write_text(
            '"""mod."""\n\n\n'
            "def good(image):\n"
            '    """Do a thing.\n\n'
            "    Parameters\n    ----------\n    image : ndarray\n        x.\n\n"
            "    Returns\n    -------\n    out : ndarray\n        y.\n"
            '    """\n'
            "    return image\n"
        )
        result = check_workspace(tmp_path, profile)
        doc_violations = [v for v in result.violations if v.rule_id == "SK-DOC-001"]
        assert doc_violations
        assert any("Examples" in v.message for v in doc_violations)


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

    def test_non_utf8_file_does_not_crash(self, tmp_path, profile):
        """A non-UTF-8 source file is skipped, not fatal (xm1.3)."""
        (tmp_path / "_weird.py").write_bytes(b"\xff\xfe\x00not valid utf-8\n")
        result = check_workspace(tmp_path, profile)
        assert result is not None
