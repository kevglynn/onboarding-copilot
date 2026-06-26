"""Pydantic models for library convention profiles."""

from pydantic import BaseModel, Field


class TestConventions(BaseModel):
    """Testing conventions for the library."""

    framework: str = Field(description="Test framework name (e.g., pytest)")
    file_pattern: str = Field(description="Test file naming pattern (e.g., test_*.py)")
    location_pattern: str = Field(
        description="Where tests live relative to source (e.g., {module}/tests/)"
    )
    required_patterns: list[str] = Field(
        default_factory=list,
        description="Patterns every test file must include (e.g., shape preservation)",
    )
    run_command: str = Field(
        default="pytest",
        description="Command to run tests (e.g., spin test, pytest)",
    )


class DeprecatedAPI(BaseModel):
    """A deprecated API entry with replacement guidance."""

    symbol: str = Field(description="Fully qualified deprecated symbol")
    replacement: str = Field(description="Recommended replacement")
    reason: str = Field(default="", description="Why it was deprecated")
    since_version: str = Field(default="", description="Version when deprecated")


class DocstringConvention(BaseModel):
    """Docstring format requirements."""

    style: str = Field(description="Docstring style: numpydoc, google, sphinx")
    required_sections: list[str] = Field(
        default_factory=lambda: ["Parameters", "Returns"],
        description="Sections every public function docstring must have",
    )
    array_shape_notation: bool = Field(
        default=False,
        description="Whether array params require shape notation like (M, N)",
    )


class RoleBriefTemplate(BaseModel):
    """Template sections for a specific role's brief."""

    role: str = Field(description="Role name: engineer, pm, qa, devops")
    sections: list[str] = Field(description="Section headings for this role's brief")
    focus: str = Field(description="What this role cares about most")


class LibraryProfile(BaseModel):
    """Convention profile for an open-source library.

    This is the architectural core of the copilot. Everything —
    the CLI, the Cursor rules, and the MCP server — reads from
    this schema. The team owns the YAML; the engine owns the logic.
    """

    name: str = Field(description="Library display name")
    version: str = Field(description="Profile schema version")
    description: str = Field(description="One-line library description")
    language: str = Field(default="python", description="Primary language")

    approved_directories: list[str] = Field(
        description="Directories where new code is allowed"
    )
    forbidden_paths: list[str] = Field(
        description="Paths that must never be imported from or written to"
    )

    test_conventions: TestConventions
    deprecated_apis: list[DeprecatedAPI] = Field(default_factory=list)
    docstring_convention: DocstringConvention

    contribution_checklist: list[str] = Field(
        default_factory=list,
        description="Steps every contribution must complete",
    )
    role_brief_templates: list[RoleBriefTemplate] = Field(
        default_factory=list,
        description="Per-role brief structure definitions",
    )

    naming_convention: str = Field(
        default="snake_case",
        description="Function/variable naming convention",
    )
    import_convention: str = Field(
        default="",
        description="Canonical import pattern (e.g., import skimage as ski)",
    )
