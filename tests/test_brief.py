"""Tests for the brief command."""

import pytest

from ob.commands.brief import VALID_ROLES, generate_brief
from ob.profile import load_profile


@pytest.fixture
def profile(scikit_image_profile_path):
    return load_profile(scikit_image_profile_path)


class TestBriefGeneration:
    """Tests for brief content generation."""

    def test_engineer_brief_has_checklist(self, examples_dir, profile):
        """Engineer brief contains implementation checklist."""
        brief = generate_brief("engineer", examples_dir / "safe-first-contrib", profile)
        assert "Checklist" in brief
        assert "Naming" in brief or "naming" in brief

    def test_pm_brief_has_scope(self, examples_dir, profile):
        """PM brief contains scope information."""
        brief = generate_brief("pm", examples_dir / "safe-first-contrib", profile)
        assert "Scope" in brief
        assert "Impact" in brief or "impact" in brief

    def test_qa_brief_has_test_strategy(self, examples_dir, profile):
        """QA brief contains test strategy."""
        brief = generate_brief("qa", examples_dir / "safe-first-contrib", profile)
        assert "Test Strategy" in brief
        assert "Edge Cases" in brief

    def test_devops_brief_has_ci_guardrails(self, examples_dir, profile):
        """DevOps brief contains CI guardrails."""
        brief = generate_brief("devops", examples_dir / "safe-first-contrib", profile)
        assert "CI Guardrails" in brief
        assert "Pipeline Signal" in brief

    def test_briefs_are_meaningfully_different(self, examples_dir, profile):
        """All four briefs have different content."""
        briefs = {
            role: generate_brief(role, examples_dir / "safe-first-contrib", profile)
            for role in VALID_ROLES
        }
        contents = list(briefs.values())
        for i, a in enumerate(contents):
            for b in contents[i + 1 :]:
                assert a != b, "Two briefs are identical"

    def test_invalid_role_raises(self, examples_dir, profile):
        """Unknown role raises ValueError."""
        with pytest.raises(ValueError, match="Unknown role"):
            generate_brief("ceo", examples_dir / "safe-first-contrib", profile)


class TestBriefWithEmptyWorkspace:
    """Briefs should work even with minimal workspace content."""

    def test_engineer_brief_empty_workspace(self, tmp_path, profile):
        """Engineer brief works with empty workspace."""
        brief = generate_brief("engineer", tmp_path, profile)
        assert "Engineer Brief" in brief

    def test_pm_brief_empty_workspace(self, tmp_path, profile):
        """PM brief works with empty workspace."""
        brief = generate_brief("pm", tmp_path, profile)
        assert "PM Brief" in brief

    def test_all_roles_produce_output(self, tmp_path, profile):
        """Every role produces non-empty output."""
        for role in VALID_ROLES:
            brief = generate_brief(role, tmp_path, profile)
            assert len(brief) > 100, f"{role} brief is too short"
