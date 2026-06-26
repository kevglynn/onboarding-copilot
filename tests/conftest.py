"""Shared test fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def profiles_dir():
    """Path to the profiles directory."""
    return Path(__file__).parent.parent / "profiles"


@pytest.fixture
def scikit_image_profile_path(profiles_dir):
    """Path to the scikit-image profile YAML."""
    return profiles_dir / "scikit-image.yaml"


@pytest.fixture
def diffusers_profile_path(profiles_dir):
    """Path to the diffusers stub profile YAML."""
    return profiles_dir / "diffusers.yaml"


@pytest.fixture
def examples_dir():
    """Path to the examples directory."""
    return Path(__file__).parent.parent / "examples"
