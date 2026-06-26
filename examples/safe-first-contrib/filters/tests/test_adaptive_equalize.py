"""Tests for adaptive histogram equalization helper."""

import numpy as np
import pytest

from skimage.filters._adaptive_equalize import adaptive_equalize


class TestAdaptiveEqualize:
    """Tests for the adaptive_equalize function."""

    def test_output_shape_preserved(self):
        """Output image has the same shape as the input."""
        image = np.random.default_rng(42).random((64, 64))
        result = adaptive_equalize(image)
        assert result.shape == image.shape

    def test_output_dtype_float64(self):
        """Output is always float64 per exposure module convention."""
        image = np.random.default_rng(42).random((32, 32)).astype(np.float32)
        result = adaptive_equalize(image)
        assert result.dtype == np.float64

    def test_output_range_zero_to_one(self):
        """Output values are in [0, 1] range."""
        image = np.random.default_rng(42).random((64, 64))
        result = adaptive_equalize(image)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_uniform_image_unchanged(self):
        """A uniform image should remain approximately uniform."""
        image = np.full((32, 32), 0.5)
        result = adaptive_equalize(image)
        assert np.allclose(result, result.mean(), atol=0.1)

    def test_rejects_3d_input(self):
        """Raises ValueError for non-2D input."""
        image_3d = np.random.default_rng(42).random((32, 32, 3))
        with pytest.raises(ValueError, match="2D grayscale"):
            adaptive_equalize(image_3d)

    def test_rejects_1d_input(self):
        """Raises ValueError for 1D input."""
        image_1d = np.random.default_rng(42).random((64,))
        with pytest.raises(ValueError, match="2D grayscale"):
            adaptive_equalize(image_1d)

    def test_clip_limit_out_of_range(self):
        """Raises ValueError for clip_limit outside [0, 1]."""
        image = np.random.default_rng(42).random((32, 32))
        with pytest.raises(ValueError, match="clip_limit"):
            adaptive_equalize(image, clip_limit=1.5)

    def test_custom_kernel_size(self):
        """Accepts a custom kernel_size without error."""
        image = np.random.default_rng(42).random((64, 64))
        result = adaptive_equalize(image, kernel_size=16)
        assert result.shape == (64, 64)

    def test_uint8_input_accepted(self):
        """Accepts uint8 input and returns float64 output."""
        rng = np.random.default_rng(42)
        image = rng.integers(0, 256, size=(32, 32), dtype=np.uint8)
        result = adaptive_equalize(image)
        assert result.dtype == np.float64
        assert result.shape == (32, 32)
