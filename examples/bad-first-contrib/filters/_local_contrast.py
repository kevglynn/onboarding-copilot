"""Local contrast normalization for grayscale images."""

import numpy as np
from skimage._shared.utils import _validate_interpolation_order  # noqa: F401
from skimage.filters import median


def local_contrast_normalize(image, window_size=7):
    """Normalize local contrast in a grayscale image.

    Args:
        image: Input image.
        window_size: Size of the local window.

    Returns:
        Normalized image.
    """
    # TODO: implement this
    pass
