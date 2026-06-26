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
