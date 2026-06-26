"""FastMCP server exposing library conventions to Cursor's context engine.

Run with: fastmcp run src/ob/mcp_server.py
Or:       python -m ob.mcp_server
"""

from pathlib import Path

from fastmcp import FastMCP

from ob.commands.check import check_workspace as _run_check
from ob.profile import load_profile

REPO_ROOT = Path(__file__).parent.parent.parent
PROFILE_PATH = REPO_ROOT / "profiles" / "scikit-image.yaml"

mcp = FastMCP(
    "Engineering Onboarding Copilot",
    instructions=(
        "Provides library contribution conventions, approved directories, "
        "deprecated APIs, and testing requirements loaded from the active "
        "profile YAML. Use these resources when helping engineers write or "
        "review code contributions. Use the check_workspace tool to validate "
        "a workspace against the conventions."
    ),
)


def _get_profile():
    return load_profile(PROFILE_PATH)


def check_workspace_report(path: str) -> dict:
    """Run the deterministic convention checker and return a structured report.

    Resolves a relative path against the repo root so the result is the same
    regardless of the server's working directory.
    """
    ws = Path(path)
    if not ws.is_absolute():
        ws = REPO_ROOT / ws
    result = _run_check(ws, _get_profile())
    return {
        "workspace": str(ws),
        "passed": result.passed,
        "violation_count": len(result.violations),
        "violations": [
            {
                "rule_id": v.rule_id,
                "severity": v.severity,
                "file": v.file,
                "line": v.line,
                "message": v.message,
            }
            for v in result.violations
        ],
    }


@mcp.tool
def check_workspace(path: str) -> dict:
    """Run the deterministic convention checker on a workspace.

    Mirrors the `ob check` CLI exactly — rule IDs use the profile's
    ``rule_prefix`` (e.g., ``SK-T-002`` for scikit-image, ``DIFF-T-002``
    for diffusers). Returns a structured report with ``passed``,
    ``violation_count``, and a ``violations`` list (each with ``rule_id``,
    ``severity``, ``file``, ``line``, ``message``).
    """
    return check_workspace_report(path)


@mcp.resource("conventions://approved-directories")
def get_approved_directories() -> str:
    """Directories where new source files are allowed."""
    profile = _get_profile()
    lines = ["# Approved Directories\n"]
    lines.append("New source files may only be created in these directories:\n")
    for d in profile.approved_directories:
        lines.append(f"- `{d}`")
    return "\n".join(lines)


@mcp.resource("conventions://forbidden-paths")
def get_forbidden_paths() -> str:
    """Paths that must never be imported from or written to."""
    profile = _get_profile()
    lines = ["# Forbidden Paths\n"]
    lines.append("NEVER import from or write to these paths:\n")
    for f in profile.forbidden_paths:
        lines.append(f"- `{f}`")
    return "\n".join(lines)


@mcp.resource("conventions://deprecated-apis")
def get_deprecated_apis() -> str:
    """Deprecated APIs with replacement guidance."""
    profile = _get_profile()
    lines = ["# Deprecated APIs\n"]
    lines.append("Do NOT use these APIs. Use the replacement instead.\n")
    lines.append("| Deprecated | Replacement | Reason |")
    lines.append("|-----------|-------------|--------|")
    for dep in profile.deprecated_apis:
        lines.append(f"| `{dep.symbol}` | `{dep.replacement}` | {dep.reason} |")
    return "\n".join(lines)


@mcp.resource("conventions://docstring-style")
def get_docstring_style() -> str:
    """Docstring format requirements for scikit-image."""
    profile = _get_profile()
    dc = profile.docstring_convention
    req = ", ".join(dc.required_sections)
    shape_note = (
        "REQUIRED — use `(M, N) ndarray` notation"
        if dc.array_shape_notation
        else "optional"
    )

    return f"""# Docstring Convention

- **Style:** {dc.style}
- **Required sections:** {req}
- **Array shape notation:** {shape_note}

## Template

```python
def function_name(image, param=default):
    \"\"\"One-line summary.

    Longer description if needed.

    Parameters
    ----------
    image : (M, N) ndarray
        Description of the input image.
    param : type, optional
        Description. Default is `default`.

    Returns
    -------
    result : ndarray
        Description of the output.

    Examples
    --------
    >>> from skimage.filters import function_name
    >>> result = function_name(image)
    \"\"\"
```
"""


@mcp.resource("conventions://testing")
def get_testing_conventions() -> str:
    """Testing conventions and requirements."""
    profile = _get_profile()
    tc = profile.test_conventions
    required = "\n".join(f"- {pat}" for pat in tc.required_patterns)

    return f"""# Testing Conventions

- **Framework:** {tc.framework}
- **File pattern:** `{tc.file_pattern}`
- **Location:** `{tc.location_pattern}`
- **Run command:** `{tc.run_command}`

## Required Test Patterns

{required}

## Test Naming

Good names describe what is being tested:
- `test_output_shape_preserved`
- `test_rejects_3d_input`
- `test_dtype_roundtrip`

Bad names (will be rejected):
- `test_it_works`
- `test_result`
- `test_function`
"""


@mcp.resource("conventions://contribution-checklist")
def get_contribution_checklist() -> str:
    """Complete checklist for a scikit-image contribution."""
    profile = _get_profile()
    items = "\n".join(f"- [ ] {item}" for item in profile.contribution_checklist)
    return f"""# Contribution Checklist

{items}

Run `ob check <workspace>` to validate these automatically.
"""


@mcp.resource("conventions://profile-summary")
def get_profile_summary() -> str:
    """High-level summary of the active library profile."""
    profile = _get_profile()
    return f"""# Profile: {profile.name}

{profile.description}

- **Language:** {profile.language}
- **Version:** {profile.version}
- **Naming:** {profile.naming_convention}
- **Import:** `{profile.import_convention}`
- **Approved directories:** {len(profile.approved_directories)}
- **Forbidden paths:** {len(profile.forbidden_paths)}
- **Deprecated APIs:** {len(profile.deprecated_apis)}
- **Role brief templates:** {len(profile.role_brief_templates)}

This profile is loaded from `profiles/scikit-image.yaml`.
Edit that file to update conventions.
"""


if __name__ == "__main__":
    mcp.run()
