"""Path boundary enforcement for approved workspaces and directories."""

from pathlib import Path

from ob.models import LibraryProfile


def is_approved_directory(path: str, profile: LibraryProfile) -> bool:
    """Check if a path falls within the profile's approved directories."""
    normalized = path.rstrip("/") + "/"
    return any(
        normalized.startswith(d.rstrip("/") + "/") or d.rstrip("/") + "/" == normalized
        for d in profile.approved_directories
    )


def is_forbidden_path(path: str, profile: LibraryProfile) -> bool:
    """Check if a path falls within the profile's forbidden paths."""
    normalized = path.rstrip("/") + "/"
    return any(
        normalized.startswith(f.rstrip("/") + "/") for f in profile.forbidden_paths
    )


def validate_workspace_path(workspace: str) -> Path:
    """Validate that a workspace path exists and is a directory."""
    ws = Path(workspace)
    if not ws.exists():
        raise FileNotFoundError(f"Workspace not found: {workspace}")
    if not ws.is_dir():
        raise NotADirectoryError(f"Not a directory: {workspace}")
    return ws


def extract_target_directory(task: str, profile: LibraryProfile) -> str | None:
    """Extract the target directory from a task description.

    Looks for directory-like patterns in the task string and checks
    them against the profile's approved directories.
    Returns the first matching approved directory, or None.
    """
    for approved in profile.approved_directories:
        module = approved.rstrip("/").split("/")[-1]
        if module.lower() in task.lower():
            return approved
    return None
