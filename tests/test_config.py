"""Tests for configuration dataclasses."""

import pytest
from pathlib import Path

from imagine.core.config import (
    ImageFormat,
    ImageInfo,
    ImageOrientation,
    OptimizationConfig,
    OptimizationResult,
)


def test_optimization_config_defaults():
    """Test default configuration values."""
    config = OptimizationConfig()

    assert config.target_size_kb == 100
    assert config.output_format == ImageFormat.WEBP
    assert config.min_quality == 60
    assert config.max_quality == 85
    assert config.max_dimension == 1920
    assert config.output_dir == "optimized"
    assert config.preserve_originals is True


def test_optimization_config_custom():
    """Test custom configuration values."""
    config = OptimizationConfig(
        target_size_kb=150,
        output_format=ImageFormat.JPEG,
        max_dimension=1280,
    )

    assert config.target_size_kb == 150
    assert config.output_format == ImageFormat.JPEG
    assert config.max_dimension == 1280


def test_image_info_properties():
    """Test ImageInfo computed properties."""
    info = ImageInfo(
        path=Path("test.jpg"),
        width=1920,
        height=1080,
        format="JPEG",
        mode="RGB",
        file_size_bytes=2048000,
        orientation=ImageOrientation.LANDSCAPE,
        has_transparency=False,
    )

    assert info.file_size_kb == 2000.0
    assert info.aspect_ratio == pytest.approx(1.777, rel=0.01)
    assert info.orientation == ImageOrientation.LANDSCAPE


def test_image_orientation_determination():
    """Test orientation determination from dimensions."""
    # Landscape
    info_landscape = ImageInfo(
        path=Path("test.jpg"),
        width=1920,
        height=1080,
        format="JPEG",
        mode="RGB",
        file_size_bytes=1024,
        orientation=ImageOrientation.LANDSCAPE,
        has_transparency=False,
    )
    assert info_landscape.orientation == ImageOrientation.LANDSCAPE

    # Portrait
    info_portrait = ImageInfo(
        path=Path("test.jpg"),
        width=1080,
        height=1920,
        format="JPEG",
        mode="RGB",
        file_size_bytes=1024,
        orientation=ImageOrientation.PORTRAIT,
        has_transparency=False,
    )
    assert info_portrait.orientation == ImageOrientation.PORTRAIT

    # Square
    info_square = ImageInfo(
        path=Path("test.jpg"),
        width=1080,
        height=1080,
        format="JPEG",
        mode="RGB",
        file_size_bytes=1024,
        orientation=ImageOrientation.SQUARE,
        has_transparency=False,
    )
    assert info_square.orientation == ImageOrientation.SQUARE


def test_optimization_result_properties():
    """Test OptimizationResult computed properties."""
    result = OptimizationResult(
        input_path=Path("input.jpg"),
        output_path=Path("output.webp"),
        success=True,
        original_size_bytes=2048000,
        original_width=1920,
        original_height=1080,
        original_format="JPEG",
        optimized_size_bytes=98304,  # 96 KB
        optimized_width=1920,
        optimized_height=1080,
        optimized_format="webp",
        final_quality=75,
        iterations=3,
    )

    assert result.original_size_kb == 2000.0
    assert result.optimized_size_kb == 96.0
    assert result.size_reduction_percent == pytest.approx(95.2, rel=0.1)
    assert result.dimension_scale == pytest.approx(1.0, rel=0.01)
    assert result.success is True


def test_optimization_result_dimension_scale():
    """Test dimension scale calculation."""
    result = OptimizationResult(
        input_path=Path("input.jpg"),
        output_path=Path("output.webp"),
        success=True,
        original_size_bytes=2048000,
        original_width=1920,
        original_height=1080,
        original_format="JPEG",
        optimized_size_bytes=98304,
        optimized_width=1280,  # ~67% of original
        optimized_height=720,
        optimized_format="webp",
        final_quality=75,
        iterations=5,
    )

    # Scale should be ~0.67 (sqrt of pixel reduction)
    assert result.dimension_scale == pytest.approx(0.667, rel=0.01)
