"""Convention checker — validates a workspace against the library profile."""

import ast
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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
        _check_todo_only(src, workspace, profile, result)
        _check_forbidden_imports(src, workspace, profile, result)
        _check_deprecated_apis(src, workspace, profile, result)
        _check_docstring_style(src, workspace, profile, result)

    return result


def _rel(src: Path, workspace: Path) -> str:
    """Path relative to the workspace for clean, consistent display.

    Always renders with forward slashes (``as_posix``) so violation output is
    identical on Windows and POSIX — the rule IDs and file column match the
    documented demo output regardless of the host OS.
    """
    try:
        return src.relative_to(workspace).as_posix()
    except ValueError:
        return src.as_posix()


def _safe_read(src: Path) -> str | None:
    """Read a source file as UTF-8, returning None if it cannot be decoded.

    Binary blobs or non-UTF-8 files in a workspace should be skipped, not crash
    the whole check run.
    """
    try:
        return src.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


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
            has_test = f"test_{src.name.lstrip('_')}" in test_names
            if not has_test:
                result.violations.append(
                    Violation(
                        rule_id=f"{profile.rule_prefix}-T-002",
                        severity="error",
                        message=f"Missing test file for {src.name}",
                        file=_rel(src, workspace),
                    )
                )


def _check_todo_only(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check for TODO-only implementations (no real logic)."""
    if src.name == "__init__.py":
        return
    content = _safe_read(src)
    if content is None:
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
                        rule_id=f"{profile.rule_prefix}-I-001",
                        severity="error",
                        message=(
                            f"Function '{node.name}' has TODO-only "
                            f"implementation (no real logic)"
                        ),
                        file=_rel(src, workspace),
                        line=node.lineno,
                    )
                )


def _forbidden_import_prefixes(profile: LibraryProfile) -> list[str]:
    """Forbidden paths expressed as importable dotted-path prefixes.

    Strips the profile's ``import_root`` (e.g. ``src/``) so on-disk paths like
    ``src/diffusers/_internal/`` match dotted imports like ``diffusers._internal``.
    """
    root = profile.import_root.strip("/")
    prefixes: list[str] = []
    for forbidden in profile.forbidden_paths:
        path = forbidden.strip("/")
        if root and (path == root or path.startswith(root + "/")):
            path = path[len(root) :].strip("/")
        if path:
            prefixes.append(path)
    return prefixes


def _import_is_forbidden(module: str, prefixes: list[str]) -> bool:
    """Whether a dotted import path falls under any forbidden prefix."""
    module_path = module.replace(".", "/")
    return any(
        module_path == prefix or module_path.startswith(prefix + "/")
        for prefix in prefixes
    )


def _imported_modules(tree: ast.AST) -> list[tuple[str, int]]:
    """All imported dotted module paths with their line numbers.

    Covers both ``import a.b.c`` and ``from a.b import c`` so a forbidden
    module is caught regardless of the import form used.
    """
    modules: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append((node.module, node.lineno))
    return modules


def _check_forbidden_imports(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check for imports from forbidden/private modules (any import form)."""
    content = _safe_read(src)
    if content is None:
        return
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    prefixes = _forbidden_import_prefixes(profile)
    for module, lineno in _imported_modules(tree):
        if _import_is_forbidden(module, prefixes):
            result.violations.append(
                Violation(
                    rule_id=f"{profile.rule_prefix}-F-001",
                    severity="error",
                    message=f"Import from forbidden module: {module}",
                    file=_rel(src, workspace),
                    line=lineno,
                )
            )


def _dotted_name(node: ast.AST) -> str | None:
    """Reconstruct a dotted name (e.g. ``ski.filters.median``) from an AST node."""
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _import_bindings(tree: ast.AST) -> tuple[dict[str, str], dict[str, str]]:
    """Map locally-bound names back to their fully-qualified targets.

    Returns (module_aliases, symbol_aliases):
      - ``import skimage as ski``        -> module_aliases['ski'] = 'skimage'
      - ``from skimage.filters import median`` ->
            symbol_aliases['median'] = 'skimage.filters.median'
    """
    module_aliases: dict[str, str] = {}
    symbol_aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    module_aliases[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    module_aliases[top] = top
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                bound = alias.asname or alias.name
                symbol_aliases[bound] = f"{node.module}.{alias.name}"
    return module_aliases, symbol_aliases


def _resolve_dotted(
    dotted: str, module_aliases: dict[str, str], symbol_aliases: dict[str, str]
) -> str | None:
    """Resolve a dotted name to its fully-qualified form using import bindings."""
    head, _, rest = dotted.partition(".")
    if head in module_aliases:
        base = module_aliases[head]
        return f"{base}.{rest}" if rest else base
    if dotted in symbol_aliases:
        return symbol_aliases[dotted]
    if head in symbol_aliases:
        base = symbol_aliases[head]
        return f"{base}.{rest}" if rest else base
    return None


def _check_deprecated_apis(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Flag deprecated APIs, whether imported or used as attribute access.

    Catches three idioms: ``from m import sym``, ``import m as a; a...sym(...)``,
    and ``import pkg as p; p.sub.sym(...)`` — not just the import line.
    """
    if not profile.deprecated_apis:
        return
    content = _safe_read(src)
    if content is None:
        return
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    symbols = {dep.symbol: dep for dep in profile.deprecated_apis}
    module_aliases, symbol_aliases = _import_bindings(tree)
    seen: set[tuple[str, int]] = set()

    def flag(symbol: str, line: int) -> None:
        if (symbol, line) in seen:
            return
        seen.add((symbol, line))
        dep = symbols[symbol]
        result.violations.append(
            Violation(
                rule_id=f"{profile.rule_prefix}-D-001",
                severity="warning",
                message=(f"Deprecated API: {symbol} — use {dep.replacement} instead"),
                file=_rel(src, workspace),
                line=line,
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                full = f"{node.module}.{alias.name}"
                if full in symbols:
                    flag(full, node.lineno)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in symbols:
                    flag(alias.name, node.lineno)
        elif isinstance(node, (ast.Attribute, ast.Name)):
            dotted = _dotted_name(node)
            if dotted is None:
                continue
            resolved = _resolve_dotted(dotted, module_aliases, symbol_aliases)
            if resolved in symbols:
                flag(resolved, node.lineno)


def _check_docstring_style(
    src: Path, workspace: Path, profile: LibraryProfile, result: CheckResult
) -> None:
    """Check docstrings match the profile's style and required sections.

    Emits at most one DOC-001 per function: a style mismatch takes precedence
    (fix the style first), otherwise missing required sections are reported.
    Works for any style — numpydoc, google, etc. — via the profile.
    """
    content = _safe_read(src)
    if content is None:
        return
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    style = profile.docstring_convention.style
    required = profile.docstring_convention.required_sections
    prefix = profile.rule_prefix

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            continue

        if style == "numpydoc" and ("Args:" in docstring or "Arguments:" in docstring):
            result.violations.append(
                Violation(
                    rule_id=f"{prefix}-DOC-001",
                    severity="warning",
                    message=(
                        f"Function '{node.name}' uses Google-style "
                        f"docstring (Args:) — expected numpydoc (Parameters:)"
                    ),
                    file=_rel(src, workspace),
                    line=node.lineno,
                )
            )
            continue

        missing = [section for section in required if section not in docstring]
        if missing:
            result.violations.append(
                Violation(
                    rule_id=f"{prefix}-DOC-001",
                    severity="warning",
                    message=(
                        f"Function '{node.name}' docstring is missing required "
                        f"section(s): {', '.join(missing)}"
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
