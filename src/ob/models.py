"""Pydantic models for library convention profiles."""

from pydantic import BaseModel, ConfigDict, Field


class TestConventions(BaseModel):
    """Testing conventions for the library."""

    model_config = ConfigDict(extra="forbid")

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

    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(description="Fully qualified deprecated symbol")
    replacement: str = Field(description="Recommended replacement")
    reason: str = Field(default="", description="Why it was deprecated")


class DocstringConvention(BaseModel):
    """Docstring format requirements."""

    model_config = ConfigDict(extra="forbid")

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

    model_config = ConfigDict(extra="forbid")

    role: str = Field(description="Role name: engineer, pm, qa, devops")
    sections: list[str] = Field(description="Section headings for this role's brief")
    focus: str = Field(description="What this role cares about most")


class LibraryProfile(BaseModel):
    """Convention profile for an open-source library.

    This is the architectural core of the copilot. Everything —
    the CLI, the Cursor rules, and the MCP server — reads from
    this schema. The team owns the YAML; the engine owns the logic.
    """

    model_config = ConfigDict(extra="forbid")

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
    import_root: str = Field(
        default="",
        description=(
            "Filesystem prefix that is NOT part of the import path "
            "(e.g. 'src/' for a src-layout repo). Stripped from forbidden_paths "
            "when matching against dotted import statements, so "
            "'src/diffusers/_internal/' correctly flags 'import diffusers._internal'."
        ),
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

    rule_prefix: str = Field(
        default="SK",
        description=(
            "Namespace prefix for violation rule IDs (e.g., 'SK' -> SK-T-002). "
            "Profile-owned so swapping the YAML renames the rule catalog, "
            "proving the engine is not hardcoded to one library."
        ),
    )

    default_directory: str = Field(
        default="",
        description="Fallback approved directory when no keyword/module matches",
    )
    directory_keywords: dict[str, list[str]] = Field(
        default_factory=dict,
        description=(
            "Map of module name -> task keywords that route a scaffold there. "
            "Keywords match on a word boundary, so prefixes like 'equaliz' "
            "match 'equalization' without false substring hits."
        ),
    )
