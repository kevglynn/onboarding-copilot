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
    """Convert a task description to a filesystem-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:60].rstrip("-")


def _infer_module_name(task: str) -> str:
    """Infer a Python module name from the task description."""
    slug = _slugify(task)
    return slug.replace("-", "_")


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
        target_dir = (
            profile.approved_directories[0] if profile.approved_directories else "src/"
        )

    for forbidden in profile.forbidden_paths:
        forbidden_name = forbidden.rstrip("/").split("/")[-1].lstrip("_")
        if forbidden_name.lower() in task.lower():
            return None

    workspace.mkdir(parents=True, exist_ok=True)
    _write_plan(workspace, task, target_dir, module_name, profile)
    _write_source_stub(workspace, target_dir, module_name, profile)
    _write_test_stub(workspace, target_dir, module_name, profile)
    _write_briefs_stub(workspace, task, profile)

    return workspace


def _write_plan(
    workspace: Path,
    task: str,
    target_dir: str,
    module_name: str,
    profile: LibraryProfile,
) -> None:
    """Write the PLAN.md file."""
    checklist = "\n".join(f"- [ ] {item}" for item in profile.contribution_checklist)

    content = f"""# Contribution Plan: {task.title()}

Per {profile.name} conventions, this contribution targets `{target_dir}`.

## Task
{task}

## Files to Create/Modify
- `{target_dir}_{module_name}.py` — implementation
- `{target_dir}tests/test_{module_name}.py` — tests

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

import numpy as np


def {module_name}(image):
{docstring_template}
    raise NotImplementedError("Implement {module_name}")
'''
    (src_dir / f"_{module_name}.py").write_text(content)


def _write_test_stub(
    workspace: Path,
    target_dir: str,
    module_name: str,
    profile: LibraryProfile,
) -> None:
    """Write a test file stub."""
    test_dir = workspace / target_dir.rstrip("/") / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)

    content = f'''"""Tests for {module_name}."""

import numpy as np
import pytest


class Test{module_name.replace("_", " ").title().replace(" ", "")}:
    """Tests for the {module_name} function."""

    def test_output_shape_preserved(self):
        """Output image has the same shape as the input."""
        # FIXME: Implement shape preservation test
        pytest.skip("Not yet implemented")

    def test_output_dtype_roundtrip(self):
        """Output dtype matches expected convention."""
        # FIXME: Implement dtype roundtrip test
        pytest.skip("Not yet implemented")
'''
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
