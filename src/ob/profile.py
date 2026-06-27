"""Profile loading and validation."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from ob.models import LibraryProfile

KNOWN_DOCSTRING_STYLES = {"numpydoc", "google", "sphinx"}
KNOWN_ROLES = {"engineer", "pm", "qa", "devops"}


def load_profile(path: str | Path) -> LibraryProfile:
    """Load and validate a library convention profile from YAML.

    Parameters
    ----------
    path : str or Path
        Path to the profile YAML file.

    Returns
    -------
    LibraryProfile
        Validated profile model.

    Raises
    ------
    FileNotFoundError
        If the profile file does not exist.
    pydantic.ValidationError
        If the YAML does not match the expected schema.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return LibraryProfile.model_validate(data)


def lint_profile(path: str | Path) -> list[str]:
    """Validate a profile and return a list of human-readable problems.

    Load-time errors (missing file, bad YAML, schema/extra-key violations) are
    returned as problems too, so a single call surfaces every reason a profile
    would not behave as the author intends. An empty list means the profile is
    structurally sound and internally consistent.
    """
    try:
        profile = load_profile(path)
    except FileNotFoundError as exc:
        return [str(exc)]
    except yaml.YAMLError as exc:
        return [f"Could not parse YAML: {exc}"]
    except ValidationError as exc:
        return [f"Schema error: {err['loc']}: {err['msg']}" for err in exc.errors()]

    problems: list[str] = []
    approved_leaves = {
        d.rstrip("/").split("/")[-1] for d in profile.approved_directories
    }

    if not profile.rule_prefix.strip():
        problems.append("rule_prefix is empty")

    if profile.docstring_convention.style not in KNOWN_DOCSTRING_STYLES:
        problems.append(
            f"docstring_convention.style '{profile.docstring_convention.style}' "
            f"is not one of {sorted(KNOWN_DOCSTRING_STYLES)}"
        )

    if (
        profile.default_directory
        and profile.default_directory not in profile.approved_directories
    ):
        problems.append(
            f"default_directory '{profile.default_directory}' is not in "
            f"approved_directories"
        )

    for module in profile.directory_keywords:
        if module not in approved_leaves:
            problems.append(
                f"directory_keywords module '{module}' does not match the leaf "
                f"of any approved directory"
            )

    for template in profile.role_brief_templates:
        if template.role not in KNOWN_ROLES:
            problems.append(
                f"role_brief_templates role '{template.role}' is not a known "
                f"role {sorted(KNOWN_ROLES)}"
            )

    overlap = set(profile.approved_directories) & set(profile.forbidden_paths)
    if overlap:
        problems.append(
            f"directories are both approved and forbidden: {sorted(overlap)}"
        )

    return problems
