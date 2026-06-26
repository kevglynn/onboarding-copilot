"""Convention checker — validates a workspace against the library profile."""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ob.guardrails import is_forbidden_path
from ob.models import LibraryProfile


@dataclass
class Violation:
    """A single convention violation."""

    rule_id: str
    severity: str
    message: str
    file: str = ""
    line: int = 0


@dataclass
class CheckResult:
    """Result of checking a workspace."""

    workspace: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def check_workspace(workspace: Path, profile: LibraryProfile) -> CheckResult:
    """Run all convention checks against a workspace."""
    result = CheckResult(workspace=str(workspace))

    python_files = list(workspace.rglob("*.py"))
    test_files = [f for f in python_files if f.name.startswith("test_")]
    source_files = [f for f in python_files if not f.name.startswith("test_")]

    _check_missing_tests(source_files, test_files, workspace, profile, result)
    for src in source_files:
        _check_todo_only(src, workspace, result)
        _check_forbidden_imports(src, workspace, profile, result)
        _check_deprecated_apis(src, workspace, profile, result)
        _check_docstring_style(src, workspace, profile, result)

    return result


def _rel(src: Path, workspace: Path) -> str:
    """Path relative to the workspace for clean, consistent display."""
    try:
        return str(src.relative_to(workspace))
    except ValueError:
        return str(src)


def _check_missing_tests(
    source_files: list[Path],
    test_files: list[Path],
    workspace: Path,
    profile: LibraryProfile,
    result: CheckResult,
) -> None:
    """Check that source files have corresponding test files."""
    test_names = {f.name for f in test_files}
    for src in source_files:
        if src.name.startswith("_") and src.name != "__init__.py":
            expected_test = f"test{src.name.lstrip('_')}"
            has_test = (
                f"test_{src.name.lstrip('_')}" in test_names
                or expected_test in test_names
            )
            if not has_test:
                result.violations.append(
                    Violation(
                        rule_id="SK-T-002",
                        severity="error",
                        message=f"Missing test file for {src.name}",
                        file=str(src.relative_to(workspace)),
                    )
                )


def _check_todo_only(src: Path, workspace: Path, result: CheckResult) -> None:
    """Check for TODO-only implementations (no real logic)."""
    content = src.read_text()
    if src.name == "__init__.py":
        return

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            docstring_offset = 0
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstring_offset = 1

            real_body = body[docstring_offset:]
            if not real_body:
                continue

            is_todo = all(
                (isinstance(stmt, ast.Pass))
                or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                or (isinstance(stmt, ast.Return) and stmt.value is None)
                for stmt in real_body
            )

            if is_todo and "TODO" in content:
                result.violations.append(
                    Violation(
                        rule_id="SK-I-001",
                        severity="error",
                        message=(
                            f"Function '{node.name}' has TODO-only "
                            f"implementation (no real logic)"
                        ),
                        file=_rel(src, workspace),
                        line=node.lineno,
                    )
                )


def _check_forbidden_imports(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check for imports from forbidden/private modules."""
    content = src.read_text()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            module_path = node.module.replace(".", "/") + "/"
            if is_forbidden_path(module_path, profile):
                result.violations.append(
                    Violation(
                        rule_id="SK-F-001",
                        severity="error",
                        message=(f"Import from forbidden module: {node.module}"),
                        file=_rel(src, workspace),
                        line=node.lineno,
                    )
                )


def _check_deprecated_apis(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check for usage of deprecated APIs."""
    content = src.read_text()
    for dep in profile.deprecated_apis:
        parts = dep.symbol.rsplit(".", 1)
        if len(parts) == 2:
            module, name = parts
            pattern = rf"from\s+{re.escape(module)}\s+import\s+.*\b{re.escape(name)}\b"
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line):
                    result.violations.append(
                        Violation(
                            rule_id="SK-D-001",
                            severity="warning",
                            message=(
                                f"Deprecated API: {dep.symbol} — "
                                f"use {dep.replacement} instead"
                            ),
                            file=_rel(src, workspace),
                            line=i,
                        )
                    )


def _check_docstring_style(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check docstring style matches profile convention."""
    if profile.docstring_convention.style != "numpydoc":
        return

    content = src.read_text()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            if not docstring:
                continue
            if "Args:" in docstring or "Arguments:" in docstring:
                result.violations.append(
                    Violation(
                        rule_id="SK-DOC-001",
                        severity="warning",
                        message=(
                            f"Function '{node.name}' uses Google-style "
                            f"docstring (Args:) — expected numpydoc "
                            f"(Parameters:)"
                        ),
                        file=_rel(src, workspace),
                        line=node.lineno,
                    )
                )


def render_check_result(result: CheckResult, console: Console) -> None:
    """Render check results to the console with Rich formatting."""
    if result.passed:
        console.print(
            Panel(
                f"[bold green]All checks passed[/bold green]\n"
                f"Workspace: {result.workspace}",
                title="ob check",
                border_style="green",
            )
        )
        return

    table = Table(
        title=f"Convention Violations — {result.workspace}",
        show_lines=True,
    )
    table.add_column("Rule", style="bold red", width=11, no_wrap=True)
    table.add_column("Severity", width=9, no_wrap=True)
    table.add_column("File", style="cyan", overflow="fold")
    table.add_column("Message", overflow="fold")

    for v in result.violations:
        severity_style = "red" if v.severity == "error" else "yellow"
        file_loc = v.file
        if v.line:
            file_loc += f":{v.line}"
        table.add_row(
            v.rule_id,
            f"[{severity_style}]{v.severity}[/{severity_style}]",
            file_loc,
            v.message,
        )

    console.print(table)
    console.print(f"\n[bold red]{len(result.violations)} violation(s) found[/bold red]")


def render_check_result_markdown(result: CheckResult) -> str:
    """Render check results as markdown."""
    if result.passed:
        return f"## ob check: {result.workspace}\n\nAll checks passed.\n"

    lines = [f"## ob check: {result.workspace}\n"]
    lines.append(f"**{len(result.violations)} violation(s) found**\n")
    lines.append("| Rule | Severity | File | Message |")
    lines.append("|------|----------|------|---------|")
    for v in result.violations:
        file_loc = v.file
        if v.line:
            file_loc += f":{v.line}"
        lines.append(f"| {v.rule_id} | {v.severity} | {file_loc} | {v.message} |")
    return "\n".join(lines) + "\n"
