"""CLI entry point for the Engineering Onboarding Copilot."""

import typer
from rich.console import Console

from ob import __version__
from ob.commands.brief import VALID_ROLES, generate_brief, render_brief
from ob.commands.check import check_workspace, render_check_result
from ob.commands.scaffold import render_scaffold_result, scaffold_workspace
from ob.guardrails import validate_workspace_path
from ob.profile import load_profile

app = typer.Typer(
    name="ob",
    help="Engineering Onboarding Copilot — convention-aware SDLC workflow.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool):
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
):
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
        "profiles/scikit-image.yaml",
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
):
    """Create a new contribution workspace with starter files."""
    profile = load_profile(profile_path)
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
        "profiles/scikit-image.yaml",
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
):
    """Validate a workspace against the library profile conventions."""
    ws = validate_workspace_path(workspace)
    profile = load_profile(profile_path)
    result = check_workspace(ws, profile)
    render_check_result(result, console)
    if not result.passed:
        raise typer.Exit(code=1)


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
        "profiles/scikit-image.yaml",
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
):
    """Generate a role-specific brief for the contribution."""
    if role not in VALID_ROLES:
        console.print(
            f"[bold red]Unknown role:[/bold red] {role}\n"
            f"Valid roles: {', '.join(sorted(VALID_ROLES))}"
        )
        raise typer.Exit(code=1)

    ws = validate_workspace_path(workspace)
    profile = load_profile(profile_path)
    content = generate_brief(role, ws, profile)
    render_brief(content, role, console, output_format=format)
