"""Brief command — generates role-specific briefs from workspace metadata."""

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from ob.models import LibraryProfile

VALID_ROLES = {"engineer", "pm", "qa", "devops"}


def generate_brief(
    role: str,
    workspace: Path,
    profile: LibraryProfile,
) -> str:
    """Generate a role-specific brief in markdown format.

    Each role gets a meaningfully different perspective on the same
    workspace — not four copies of the same content.
    """
    if role not in VALID_ROLES:
        raise ValueError(
            f"Unknown role '{role}'. Valid roles: {', '.join(sorted(VALID_ROLES))}"
        )

    workspace_name = workspace.name
    python_files = list(workspace.rglob("*.py"))
    test_files = [f for f in python_files if f.name.startswith("test_")]
    source_files = [f for f in python_files if not f.name.startswith("test_")]
    plan_file = workspace / "PLAN.md"
    has_plan = plan_file.exists()

    generators = {
        "engineer": _engineer_brief,
        "pm": _pm_brief,
        "qa": _qa_brief,
        "devops": _devops_brief,
    }

    return generators[role](
        workspace_name=workspace_name,
        workspace=workspace,
        source_files=source_files,
        test_files=test_files,
        has_plan=has_plan,
        profile=profile,
    )


def _engineer_brief(
    workspace_name: str,
    workspace: Path,
    source_files: list[Path],
    test_files: list[Path],
    has_plan: bool,
    profile: LibraryProfile,
) -> str:
    """Generate the engineer's implementation-focused brief."""
    file_map = "\n".join(
        f"  - `{f.relative_to(workspace)}`" for f in sorted(source_files + test_files)
    )
    if not file_map:
        file_map = "  - _(no files yet)_"

    checklist = "\n".join(f"- [ ] {item}" for item in profile.contribution_checklist)
    req_sections = ", ".join(profile.docstring_convention.required_sections)
    shape_note = (
        "required" if profile.docstring_convention.array_shape_notation else "optional"
    )
    test_fw = profile.test_conventions.framework
    test_pat = profile.test_conventions.file_pattern

    return f"""# Engineer Brief: {workspace_name}

## Implementation Checklist

{checklist}

## File Map

{file_map}

## Convention Reminders

- **Naming:** {profile.naming_convention}
- **Docstrings:** {profile.docstring_convention.style} style
  - Required sections: {req_sections}
  - Array shape notation: {shape_note}
- **Tests:** {test_fw} with `{test_pat}`
  - Location: `{profile.test_conventions.location_pattern}`
  - Run with: `{profile.test_conventions.run_command}`
- **Import convention:** `{profile.import_convention}`
"""


def _pm_brief(
    workspace_name: str,
    workspace: Path,
    source_files: list[Path],
    test_files: list[Path],
    has_plan: bool,
    profile: LibraryProfile,
) -> str:
    """Generate the PM's scope-and-impact-focused brief."""
    if len(source_files) <= 2:
        scope_size = "small"
    elif len(source_files) <= 5:
        scope_size = "medium"
    else:
        scope_size = "large"
    test_count = len(test_files)

    dep_count = len(profile.deprecated_apis)
    guardrail_count = len(profile.forbidden_paths)

    return f"""# PM Brief: {workspace_name}

## Scope

- **Size:** {scope_size} ({len(source_files)} source file(s), {test_count} test file(s))
- **Target library:** {profile.name}
- **PLAN.md present:** {"Yes" if has_plan else "No — ask engineering to create one"}

## User Impact

This contribution adds new functionality to {profile.name}. The change
follows the library's established conventions and is constrained by
{guardrail_count} path boundary rule(s) and {dep_count} deprecated API guard(s).

## What to Ask in Kickoff

- Is the scope appropriately bounded for a first contribution?
- Are there existing issues or RFCs this duplicates?
- Does the naming align with existing {profile.name} module patterns?
- Has the gallery example requirement been addressed (if adding public API)?
"""


def _qa_brief(
    workspace_name: str,
    workspace: Path,
    source_files: list[Path],
    test_files: list[Path],
    has_plan: bool,
    profile: LibraryProfile,
) -> str:
    """Generate the QA's test-strategy-focused brief."""
    test_list = "\n".join(
        f"  - `{f.relative_to(workspace)}`" for f in sorted(test_files)
    )
    if not test_list:
        test_list = "  - _(no test files found — this is a blocker)_"

    required = "\n".join(
        f"- [ ] {pat}" for pat in profile.test_conventions.required_patterns
    )
    if not required:
        required = "- _(none specified in profile)_"

    return f"""# QA Brief: {workspace_name}

## Test Strategy

- **Framework:** {profile.test_conventions.framework}
- **Run command:** `{profile.test_conventions.run_command}`
- **Test files found:**
{test_list}

## Required Test Patterns

{required}

## Edge Cases to Watch

- Very small inputs (degenerate dimensions)
- NaN / Inf values in numeric arrays
- Dtype boundaries (uint8 overflow, float precision)
- Empty inputs (zero-length arrays)
- Concurrent access (if applicable)

## Test Names We Will Reject

- `test_it_works` — not descriptive
- `test_result` — doesn't specify what about the result
- `test_{workspace_name}` — just restates the module name
- `test_function` — generic, meaningless
"""


def _devops_brief(
    workspace_name: str,
    workspace: Path,
    source_files: list[Path],
    test_files: list[Path],
    has_plan: bool,
    profile: LibraryProfile,
) -> str:
    """Generate the DevOps's CI-and-boundary-focused brief."""
    approved = "\n".join(f"  - `{d}`" for d in profile.approved_directories)
    forbidden = "\n".join(f"  - `{f}`" for f in profile.forbidden_paths)

    return f"""# DevOps Brief: {workspace_name}

## CI Guardrails

- `ob check` validates convention compliance
- `{profile.test_conventions.run_command}` runs the test suite
- `ruff check` enforces style (if configured)

## Pipeline Signal

| Check | Pass | Fail |
|-------|------|------|
| `ob check` | Convention-compliant | Block merge |
| `{profile.test_conventions.run_command}` | Tests green | Block merge |
| `ruff check` | Style clean | Block merge |

## Boundary Enforcement

**Approved directories:**
{approved}

**Forbidden paths:**
{forbidden}

Files outside approved directories will be rejected by `ob scaffold`.
Imports from forbidden paths will be flagged by `ob check`.
"""


def render_brief(
    brief_content: str,
    role: str,
    console: Console,
    output_format: str = "rich",
) -> None:
    """Render a brief to the console."""
    if output_format == "markdown":
        console.print(brief_content)
        return

    console.print(
        Panel(
            Markdown(brief_content),
            title=f"ob brief — {role}",
            border_style="blue",
            padding=(1, 2),
        )
    )
