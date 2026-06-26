"""Profile loading and validation."""

from pathlib import Path

import yaml

from ob.models import LibraryProfile


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
