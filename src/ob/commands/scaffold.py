"""Scaffold command — creates a new contribution workspace from profile conventions."""

import re
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from ob.guardrails import (
    extract_target_directory,
)
from ob.models import LibraryProfile


def _slugify(text: str) -> str:
    """Convert a task description to a filesystem-safe slug.

    Falls back to ``contribution`` when the task has no slug-able characters
    (e.g. an empty or symbol-only task) so the workspace path is never blank.
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:60].strip("-") or "contribution"


def _infer_module_name(task: str) -> str:
    """Infer a valid Python module/function name from the task description.

    Guarantees a syntactically valid identifier: a digit-leading slug (e.g.
    ``123`` -> ``mod_123``) is prefixed so the generated ``def`` never breaks.
    """
    name = _slugify(task).replace("-", "_")
    if name[:1] != "_" and not name[:1].isalpha():
        name = f"mod_{name}"
    return name


def _test_dir_rel(target_dir: str, profile: LibraryProfile) -> str:
    """Resolve where tests live, honoring the profile's location_pattern.

    ``{module}`` in the pattern is the target directory with the profile's
    import_root stripped, so scikit-image ('{module}/tests/') co-locates tests
    while diffusers ('tests/{module}/') puts them under a top-level tests tree.
    """
    module_token = target_dir.rstrip("/")
    root = profile.import_root.strip("/")
    if root and (module_token == root or module_token.startswith(root + "/")):
        module_token = module_token[len(root) :].strip("/")
    pattern = profile.test_conventions.location_pattern or "{module}/tests/"
    return pattern.replace("{module}", module_token).rstrip("/")


def _test_method_name(pattern: str, seen: set[str]) -> str:
    """Turn a required-test-pattern phrase into a unique valid test method name."""
    text = re.sub(r"\btests?\b", " ", pattern.strip().lower())
    name = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    if not name:
        name = "behavior"
    if name[0].isdigit():
        name = f"n_{name}"
    candidate = f"test_{name}"
    suffix = 2
    while candidate in seen:
        candidate = f"test_{name}_{suffix}"
        suffix += 1
    seen.add(candidate)
    return candidate


def _references_forbidden_path(task: str, profile: LibraryProfile) -> bool:
    """Whether the task explicitly asks to write into a forbidden path.

    Matches the full forbidden path (e.g. ``skimage/_vendored``) or its leaf
    *with* the leading underscore (``_vendored``). Keeping the underscore is
    what prevents false refusals: a task that merely contains the prose word
    ``build`` or ``shared`` no longer collides with ``_build`` / ``_shared``.
    """
    task_lower = task.lower()
    for forbidden in profile.forbidden_paths:
        normalized = forbidden.rstrip("/")
        leaf = normalized.split("/")[-1]
        if normalized.lower() in task_lower or leaf.lower() in task_lower:
            return True
    return False


def scaffold_workspace(
    task: str,
    profile: LibraryProfile,
    base_dir: Path | None = None,
) -> Path | None:
    """Create a new contribution workspace with starter files.

    Returns the workspace path on success, None if the path is forbidden.
    """
    if base_dir is None:
        base_dir = Path("workspaces")

    slug = _slugify(task)
    module_name = _infer_module_name(task)
    workspace = base_dir / slug

    target_dir = extract_target_directory(task, profile)
    if target_dir is None:
        target_dir = profile.default_directory or (
            profile.approved_directories[0] if profile.approved_directories else "src/"
        )

    if _references_forbidden_path(task, profile):
        return None

    test_dir_rel = _test_dir_rel(target_dir, profile)

    workspace.mkdir(parents=True, exist_ok=True)
    _write_plan(workspace, task, target_dir, module_name, profile, test_dir_rel)
    _write_source_stub(workspace, target_dir, module_name, profile)
    _write_test_stub(workspace, test_dir_rel, module_name, profile)
    _write_briefs_stub(workspace, task, profile)

    return workspace


def _write_plan(
    workspace: Path,
    task: str,
    target_dir: str,
    module_name: str,
    profile: LibraryProfile,
    test_dir_rel: str,
) -> None:
    """Write the PLAN.md file."""
    checklist = "\n".join(f"- [ ] {item}" for item in profile.contribution_checklist)

    content = f"""# Contribution Plan: {task.title()}

Per {profile.name} conventions, this contribution targets `{target_dir}`.

## Task
{task}

## Files to Create/Modify
- `{target_dir}_{module_name}.py` — implementation
- `{test_dir_rel}/test_{module_name}.py` — tests

## Conventions Applied
- Naming: {profile.naming_convention}
- Docstring: {profile.docstring_convention.style}
- Import: {profile.import_convention}
- Tests: {profile.test_conventions.framework} / {profile.test_conventions.file_pattern}

## Checklist
{checklist}
"""
    (workspace / "PLAN.md").write_text(content)


def _write_source_stub(
    workspace: Path,
    target_dir: str,
    module_name: str,
    profile: LibraryProfile,
) -> None:
    """Write a source file stub."""
    src_dir = workspace / target_dir.rstrip("/")
    src_dir.mkdir(parents=True, exist_ok=True)

    if profile.docstring_convention.style == "numpydoc":
        docstring_template = '''    """FIXME: Add one-line summary.

    Parameters
    ----------
    image : (M, N) ndarray
        FIXME: Describe input.

    Returns
    -------
    result : ndarray
        FIXME: Describe output.

    Examples
    --------
    >>> # FIXME: Add usage example
    """'''
    else:
        docstring_template = '''    """FIXME: Add one-line summary.

    Args:
        image: FIXME: Describe input.

    Returns:
        FIXME: Describe output.
    """'''

    content = f'''"""{module_name.replace("_", " ").title()} for {profile.name}."""


def {module_name}(image):
{docstring_template}
    raise NotImplementedError("Implement {module_name}")
'''
    (src_dir / f"_{module_name}.py").write_text(content)


def _write_test_stub(
    workspace: Path,
    test_dir_rel: str,
    module_name: str,
    profile: LibraryProfile,
) -> None:
    """Write a test file stub with one test per required profile pattern."""
    test_dir = workspace / test_dir_rel
    test_dir.mkdir(parents=True, exist_ok=True)

    patterns = profile.test_conventions.required_patterns or ["behaves as expected"]
    seen: set[str] = set()
    methods = []
    for pattern in patterns:
        method = _test_method_name(pattern, seen)
        summary = pattern.strip().capitalize()
        methods.append(
            f"    def {method}(self):\n"
            f'        """{summary}."""\n'
            f"        # FIXME: implement this test\n"
            f'        pytest.skip("Not yet implemented")\n'
        )
    class_name = module_name.replace("_", " ").title().replace(" ", "")
    body = "\n".join(methods)

    content = f'''"""Tests for {module_name}."""

import pytest


class Test{class_name}:
    """Tests for the {module_name} function."""

{body}'''
    (test_dir / f"test_{module_name}.py").write_text(content)


def _write_briefs_stub(
    workspace: Path,
    task: str,
    profile: LibraryProfile,
) -> None:
    """Write a BRIEFS.md stub from role templates."""
    sections = [f"# Role Briefs: {task.title()}\n"]

    for template in profile.role_brief_templates:
        sections.append(f"\n## {template.role.upper()} Brief\n")
        sections.append(f"**Focus:** {template.focus}\n")
        for heading in template.sections:
            sections.append(f"\n### {heading}\n")
            sections.append("_To be completed._\n")

    (workspace / "BRIEFS.md").write_text("\n".join(sections))


def render_scaffold_result(
    workspace: Path | None,
    task: str,
    console: Console,
) -> None:
    """Render scaffold results to the console."""
    if workspace is None:
        console.print(
            Panel(
                "[bold red]Refused[/bold red]: the target directory "
                "is in the profile's forbidden paths.\n\n"
                "The profile restricts file creation to approved "
                "directories only.",
                title="ob scaffold",
                border_style="red",
            )
        )
        return

    tree = Tree(f"[bold]{workspace}[/bold]")
    for child in sorted(workspace.rglob("*")):
        if child.is_file():
            rel = child.relative_to(workspace)
            tree.add(f"[cyan]{rel}[/cyan]")

    console.print(
        Panel(
            f"[bold green]Workspace created[/bold green]\nTask: {task}",
            title="ob scaffold",
            border_style="green",
        )
    )
    console.print(tree)
