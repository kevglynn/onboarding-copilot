"""Tests for the MCP server resource endpoints."""

import asyncio

from fastmcp import Client

from ob.mcp_server import (
    get_approved_directories,
    get_contribution_checklist,
    get_deprecated_apis,
    get_docstring_style,
    get_forbidden_paths,
    get_profile_summary,
    get_testing_conventions,
    mcp,
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


class TestMCPServerRegistration:
    """The server itself registers and serves its resources over MCP."""

    def test_server_registers_all_resources(self):
        """The wired server enumerates all 7 convention resources."""

        async def _list():
            async with Client(mcp) as client:
                return await client.list_resources()

        resources = asyncio.run(_list())
        assert len(resources) >= 7
        uris = {str(r.uri) for r in resources}
        assert "conventions://profile-summary" in uris
        assert "conventions://deprecated-apis" in uris


class TestMCPCheckTool:
    """The check_workspace MCP tool runs the deterministic checker."""

    def test_tool_is_registered(self):
        """The server exposes a check_workspace tool."""

        async def _list():
            async with Client(mcp) as client:
                return await client.list_tools()

        tools = asyncio.run(_list())
        assert "check_workspace" in {t.name for t in tools}

    def test_tool_flags_bad_contrib(self):
        """Invoking the tool on bad-first-contrib returns violations."""

        async def _call():
            async with Client(mcp) as client:
                return await client.call_tool(
                    "check_workspace", {"path": "examples/bad-first-contrib"}
                )

        res = asyncio.run(_call())
        assert res.data["passed"] is False
        assert res.data["violation_count"] >= 4

    def test_tool_passes_safe_contrib(self):
        """Invoking the tool on safe-first-contrib returns no violations."""

        async def _call():
            async with Client(mcp) as client:
                return await client.call_tool(
                    "check_workspace", {"path": "examples/safe-first-contrib"}
                )

        res = asyncio.run(_call())
        assert res.data["passed"] is True
        assert res.data["violation_count"] == 0
