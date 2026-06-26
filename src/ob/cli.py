"""CLI entry point for the Engineering Onboarding Copilot."""

import typer
from rich.console import Console

from ob import __version__

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
    profile: str = typer.Option(
        "profiles/scikit-image.yaml",
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
):
    """Create a new contribution workspace with starter files."""
    console.print(f"[bold]Scaffolding workspace for:[/bold] {task}")
    console.print(f"[dim]Profile: {profile}[/dim]")
    console.print("[yellow]Not yet implemented — see bead pbq.3[/yellow]")


@app.command()
def check(
    workspace: str = typer.Argument(
        ...,
        help="Path to the workspace to check.",
    ),
    profile: str = typer.Option(
        "profiles/scikit-image.yaml",
        "--profile",
        "-p",
        help="Path to the library profile YAML.",
    ),
):
    """Validate a workspace against the library profile conventions."""
    console.print(f"[bold]Checking workspace:[/bold] {workspace}")
    console.print(f"[dim]Profile: {profile}[/dim]")
    console.print("[yellow]Not yet implemented — see bead pbq.3[/yellow]")


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
    profile: str = typer.Option(
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
    console.print(f"[bold]Generating {role} brief[/bold]")
    console.print(f"[dim]Workspace: {workspace} | Profile: {profile}[/dim]")
    console.print("[yellow]Not yet implemented — see bead pbq.3[/yellow]")
