"""Adaptive histogram equalization for grayscale images."""

import numpy as np
from skimage.exposure import equalize_adapthist


def adaptive_equalize(image, clip_limit=0.01, kernel_size=None):
    """Apply adaptive histogram equalization to a grayscale image.

    Uses Contrast Limited Adaptive Histogram Equalization (CLAHE) to
    enhance local contrast while limiting noise amplification.

    Parameters
    ----------
    image : (M, N) ndarray
        Input grayscale image.
    clip_limit : float, optional
        Clipping limit for contrast limiting, normalized between 0 and 1.
        Higher values give more contrast. Default is 0.01.
    kernel_size : int or array_like of int, optional
        Size of the local region for histogram equalization. If ``None``,
        defaults to 1/8 of the image dimensions.

    Returns
    -------
    equalized : (M, N) ndarray of float64
        Equalized image in the range [0, 1].

    Raises
    ------
    ValueError
        If ``image`` is not a 2D array.
    ValueError
        If ``clip_limit`` is not in the range [0, 1].

    Examples
    --------
    >>> import numpy as np
    >>> from skimage.filters._adaptive_equalize import adaptive_equalize
    >>> image = np.random.default_rng(0).random((64, 64))
    >>> result = adaptive_equalize(image)
    >>> result.shape
    (64, 64)
    >>> 0.0 <= result.min() and result.max() <= 1.0
    True

    References
    ----------
    .. [1] Zuiderveld, K. "Contrast Limited Adaptive Histogram
           Equalization." Graphics Gems IV, 1994, pp. 474-485.

    See Also
    --------
    skimage.exposure.equalize_adapthist : Full CLAHE implementation.
    skimage.exposure.equalize_hist : Global histogram equalization.
    """
    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D grayscale image, got {image.ndim}D array "
            f"with shape {image.shape}."
        )

    if not 0 <= clip_limit <= 1:
        raise ValueError(
            f"clip_limit must be between 0 and 1, got {clip_limit}."
        )

    return equalize_adapthist(image, kernel_size=kernel_size,
                              clip_limit=clip_limit)
