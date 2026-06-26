"""Tests for the MCP server resource endpoints."""

from ob.mcp_server import (
    get_approved_directories,
    get_contribution_checklist,
    get_deprecated_apis,
    get_docstring_style,
    get_forbidden_paths,
    get_profile_summary,
    get_testing_conventions,
)


class TestMCPResources:
    """Tests for MCP resource endpoints."""

    def test_approved_directories_returns_content(self):
        """Approved directories resource returns markdown."""
        result = get_approved_directories()
        assert "Approved Directories" in result
        assert "skimage/filters/" in result

    def test_forbidden_paths_returns_content(self):
        """Forbidden paths resource returns markdown."""
        result = get_forbidden_paths()
        assert "Forbidden" in result
        assert "skimage/_shared/" in result

    def test_deprecated_apis_returns_table(self):
        """Deprecated APIs resource returns a markdown table."""
        result = get_deprecated_apis()
        assert "Deprecated" in result
        assert "skimage.filters.median" in result
        assert "Replacement" in result

    def test_docstring_style_returns_template(self):
        """Docstring style resource returns numpydoc template."""
        result = get_docstring_style()
        assert "numpydoc" in result
        assert "Parameters" in result
        assert "(M, N)" in result

    def test_testing_conventions_returns_content(self):
        """Testing conventions resource returns framework info."""
        result = get_testing_conventions()
        assert "pytest" in result
        assert "shape preservation" in result.lower()

    def test_contribution_checklist_returns_items(self):
        """Contribution checklist returns actionable items."""
        result = get_contribution_checklist()
        assert "Checklist" in result
        assert "- [ ]" in result

    def test_profile_summary_returns_overview(self):
        """Profile summary returns high-level overview."""
        result = get_profile_summary()
        assert "scikit-image" in result
        assert "snake_case" in result


class TestMCPResourceConsistency:
    """Cross-resource consistency checks."""

    def test_deprecated_apis_match_profile(self):
        """Deprecated APIs in MCP match the profile YAML."""
        result = get_deprecated_apis()
        assert "skimage.filters.median" in result
        assert "skimage.measure.marching_cubes_lewiner" in result
        assert "skimage.transform.estimate_transform" in result

    def test_approved_dirs_count(self):
        """MCP lists all approved directories from profile."""
        result = get_approved_directories()
        assert result.count("skimage/") >= 15
