"""Tests for the CLI entry point."""

from typer.testing import CliRunner

from ob.cli import app

runner = CliRunner()


class TestCLIBasics:
    """Tests for CLI entry point behavior."""

    def test_help(self):
        """--help exits 0 and shows commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "scaffold" in result.output
        assert "check" in result.output
        assert "brief" in result.output

    def test_version(self):
        """--version prints version string."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "ob version" in result.output

    def test_check_bad_contrib(self):
        """ob check on bad-first-contrib exits non-zero."""
        result = runner.invoke(app, ["check", "examples/bad-first-contrib"])
        assert result.exit_code != 0

    def test_check_safe_contrib(self):
        """ob check on safe-first-contrib exits zero."""
        result = runner.invoke(app, ["check", "examples/safe-first-contrib"])
        assert result.exit_code == 0

    def test_brief_engineer(self):
        """ob brief --role engineer produces output."""
        result = runner.invoke(
            app,
            [
                "brief",
                "--role",
                "engineer",
                "--workspace",
                "examples/safe-first-contrib",
            ],
        )
        assert result.exit_code == 0

    def test_brief_invalid_role(self):
        """ob brief with invalid role exits non-zero."""
        result = runner.invoke(
            app,
            ["brief", "--role", "ceo", "--workspace", "examples/safe-first-contrib"],
        )
        assert result.exit_code != 0

    def test_scaffold_forbidden_path(self):
        """ob scaffold to forbidden path exits non-zero."""
        result = runner.invoke(
            app,
            ["scaffold", "--task", "add helper to skimage/_vendored/"],
        )
        assert result.exit_code != 0


class TestLintProfileCommand:
    """The lint-profile command validates a profile and exits accordingly."""

    def test_lint_profile_scikit_image_ok(self):
        result = runner.invoke(app, ["lint-profile", "profiles/scikit-image.yaml"])
        assert result.exit_code == 0

    def test_lint_profile_diffusers_ok(self):
        result = runner.invoke(app, ["lint-profile", "profiles/diffusers.yaml"])
        assert result.exit_code == 0

    def test_lint_profile_invalid_exits_nonzero(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("name: only-a-name\n")
        result = runner.invoke(app, ["lint-profile", str(bad)])
        assert result.exit_code == 1


class TestCLIErrorHandling:
    """Bad inputs produce a friendly message and clean exit, not a traceback."""

    def test_check_missing_workspace_friendly(self):
        """ob check on a missing path exits 1 with a friendly error."""
        result = runner.invoke(app, ["check", "/no/such/path/xyz123"])
        assert result.exit_code == 1
        assert "Error" in result.output
        assert not isinstance(result.exception, FileNotFoundError)

    def test_check_missing_profile_friendly(self):
        """ob check with a missing profile exits 1 with a friendly error."""
        result = runner.invoke(
            app,
            [
                "check",
                "examples/safe-first-contrib",
                "--profile",
                "does-not-exist.yaml",
            ],
        )
        assert result.exit_code == 1
        assert "Error" in result.output
        assert not isinstance(result.exception, FileNotFoundError)

    def test_check_malformed_profile_friendly(self, tmp_path):
        """ob check with a schema-invalid profile exits 1 with a friendly error."""
        bad = tmp_path / "bad.yaml"
        bad.write_text("name: just-a-name\n")
        result = runner.invoke(
            app,
            ["check", "examples/safe-first-contrib", "--profile", str(bad)],
        )
        assert result.exit_code == 1
        assert "Error" in result.output
