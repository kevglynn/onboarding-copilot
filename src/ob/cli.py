"""CLI entry point for the Engineering Onboarding Copilot."""

from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from ob import __version__
from ob.commands.brief import VALID_ROLES, generate_brief, render_brief
from ob.commands.check import check_workspace, render_check_result
from ob.commands.scaffold import render_scaffold_result, scaffold_workspace
from ob.guardrails import validate_workspace_path
from ob.models import LibraryProfile
from ob.profile import lint_profile as _lint_profile
from ob.profile import load_profile

# Resolve the default profile against the repo root, not the current working
# directory, so `ob` works from anywhere (matches the MCP server's behavior).
# An explicit --profile is still honored as-passed (cwd-relative or absolute).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PROFILE = str(REPO_ROOT / "profiles" / "scikit-image.yaml")

app = typer.Typer(
    name="ob",
    help="Engineering Onboarding Copilot — convention-aware SDLC workflow.",
    no_args_is_help=True,
)
console = Console()


def _exit_error(message: str) -> typer.Exit:
    """Print a friendly one-line error and return an Exit(1) to raise.

    Keeps user-facing failures readable — no Python traceback for an expected
    bad-input case (missing path, malformed profile).
    """
    console.print(f"[bold red]Error:[/bold red] {message}")
    return typer.Exit(code=1)


def _load_profile_or_exit(profile_path: str) -> LibraryProfile:
    try:
        return load_profile(profile_path)
    except FileNotFoundError:
        raise _exit_error(f"Profile not found: {profile_path}")
    except yaml.YAMLError as exc:
        raise _exit_error(f"Could not parse profile YAML {profile_path}: {exc}")
    except ValidationError as exc:
        count = len(exc.errors())
        raise _exit_error(
            f"Invalid profile {profile_path} — {count} schema problem(s):\n{exc}"
        )


def _validate_workspace_or_exit(workspace: str) -> Path:
    try:
        return validate_workspace_path(workspace)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise _exit_error(str(exc))


def version_callback(value: bool) -> None:
    if value:
        console.print(f"ob version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Engineering Onboarding Copilot — convention-aware SDLC workflow."""


@app.command()
def scaffold(
    task: str = typer.Option(
        ...,
        "--task",
        "-t",
        help="Description of the contribution task.",
    ),
    profile_path: str = typer.Option(
        DEFAULT_PROFILE,
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
) -> None:
    """Create a new contribution workspace with starter files."""
    profile = _load_profile_or_exit(profile_path)
    workspace = scaffold_workspace(task, profile)
    render_scaffold_result(workspace, task, console)
    if workspace is None:
        raise typer.Exit(code=1)


@app.command()
def check(
    workspace: str = typer.Argument(
        ...,
        help="Path to the workspace to check.",
    ),
    profile_path: str = typer.Option(
        DEFAULT_PROFILE,
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
) -> None:
    """Validate a workspace against the library profile conventions."""
    ws = _validate_workspace_or_exit(workspace)
    profile = _load_profile_or_exit(profile_path)
    result = check_workspace(ws, profile)
    render_check_result(result, console)
    if not result.passed:
        raise typer.Exit(code=1)


@app.command(name="lint-profile")
def lint_profile(
    profile_path: str = typer.Argument(
        ...,
        help="Path to the library profile YAML to validate.",
    ),
) -> None:
    """Validate a library profile for schema and internal consistency."""
    problems = _lint_profile(profile_path)
    if problems:
        console.print(
            f"[bold red]Profile has {len(problems)} problem(s):[/bold red] "
            f"{profile_path}"
        )
        for problem in problems:
            console.print(f"  [red]•[/red] {problem}")
        raise typer.Exit(code=1)
    console.print(f"[bold green]Profile is valid:[/bold green] {profile_path}")


@app.command()
def brief(
    role: str = typer.Option(
        ...,
        "--role",
        "-r",
        help="Target role: engineer, pm, qa, or devops.",
    ),
    workspace: str = typer.Option(
        ".",
        "--workspace",
        "-w",
        help="Path to the workspace.",
    ),
    profile_path: str = typer.Option(
        DEFAULT_PROFILE,
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
    format: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich (terminal) or markdown.",
    ),
) -> None:
    """Generate a role-specific brief for the contribution."""
    if role not in VALID_ROLES:
        console.print(
            f"[bold red]Unknown role:[/bold red] {role}\n"
            f"Valid roles: {', '.join(sorted(VALID_ROLES))}"
        )
        raise typer.Exit(code=1)

    ws = _validate_workspace_or_exit(workspace)
    profile = _load_profile_or_exit(profile_path)
    content = generate_brief(role, ws, profile)
    render_brief(content, role, console, output_format=format)
