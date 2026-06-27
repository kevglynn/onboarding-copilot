"""Tests for the profile -> Cursor-rule generator (xm1.6)."""

from ob.profile import load_profile
from ob.render_rules import DEFAULT_RULES_DIR, render_rule, rule_output_path


class TestRenderRules:
    """The Cursor convention rule is generated from the profile, not hand-kept."""

    def test_generated_rule_matches_checked_in_file(self, scikit_image_profile_path):
        """The checked-in .mdc reproduces byte-for-byte from the profile.

        This is the local mirror of the CI drift gate: if someone edits the
        profile without regenerating, this fails.
        """
        profile = load_profile(scikit_image_profile_path)
        rendered = render_rule(profile)
        out_path = rule_output_path(profile, DEFAULT_RULES_DIR)
        assert out_path.exists()
        assert out_path.read_text(encoding="utf-8") == rendered

    def test_profile_change_changes_output(
        self, scikit_image_profile_path, diffusers_profile_path
    ):
        """Swapping the profile changes the rule — it is not a frozen copy."""
        sk = render_rule(load_profile(scikit_image_profile_path))
        diff = render_rule(load_profile(diffusers_profile_path))
        assert sk != diff
        assert "DIFF-" in diff
        assert "SK-" not in diff

    def test_generated_banner_present(self, scikit_image_profile_path):
        """The output declares its generated provenance (no false claim)."""
        rendered = render_rule(load_profile(scikit_image_profile_path))
        assert "GENERATED FROM profiles/scikit-image.yaml" in rendered
