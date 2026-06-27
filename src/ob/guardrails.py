"""Path boundary enforcement for approved workspaces and directories."""

import re
from pathlib import Path

from ob.models import LibraryProfile


def validate_workspace_path(workspace: str) -> Path:
    """Validate that a workspace path exists and is a directory."""
    ws = Path(workspace)
    if not ws.exists():
        raise FileNotFoundError(f"Workspace not found: {workspace}")
    if not ws.is_dir():
        raise NotADirectoryError(f"Not a directory: {workspace}")
    return ws


def _module_to_dir(module: str, profile: LibraryProfile) -> str | None:
    """Find the approved directory whose last path segment is `module`."""
    for approved in profile.approved_directories:
        if approved.rstrip("/").split("/")[-1] == module:
            return approved
    return None


def extract_target_directory(task: str, profile: LibraryProfile) -> str | None:
    """Infer the target approved directory for a scaffold task.

    Deterministic, first-match-wins:
    1. Profile keyword hints (module -> keywords), matched on a word boundary
       so prefixes like "equaliz" match "equalization" WITHOUT false substring
       hits — e.g. "io" no longer matches inside "equalizatION".
    2. An approved module name appearing as a whole word in the task.

    Returns None if nothing matches; the caller supplies a default.
    """
    task_lower = task.lower()

    for module, keywords in profile.directory_keywords.items():
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword.lower()), task_lower):
                target = _module_to_dir(module, profile)
                if target:
                    return target

    for approved in profile.approved_directories:
        module = approved.rstrip("/").split("/")[-1]
        if re.search(r"\b" + re.escape(module.lower()) + r"\b", task_lower):
            return approved

    return None
