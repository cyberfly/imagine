"""Tests for image analyzer."""

import pytest
from pathlib import Path
from PIL import Image
import tempfile

from imagine.core.analyzer import (
    analyze,
    _determine_orientation,
    _get_actual_dimensions,
)
from imagine.core.config import ImageOrientation


def test_determine_orientation():
    """Test orientation determination."""
    assert _determine_orientation(1920, 1080) == ImageOrientation.LANDSCAPE
    assert _determine_orientation(1080, 1920) == ImageOrientation.PORTRAIT
    assert _determine_orientation(1080, 1080) == ImageOrientation.SQUARE


def test_get_actual_dimensions():
    """Test EXIF orientation dimension handling."""
    # Normal orientations (1-4) don't swap
    assert _get_actual_dimensions(1920, 1080, 1) == (1920, 1080)
    assert _get_actual_dimensions(1920, 1080, 3) == (1920, 1080)

    # Rotated orientations (5-8) swap dimensions
    assert _get_actual_dimensions(1920, 1080, 6) == (1080, 1920)
    assert _get_actual_dimensions(1920, 1080, 8) == (1080, 1920)

    # No EXIF orientation
    assert _get_actual_dimensions(1920, 1080, None) == (1920, 1080)


def test_analyze_creates_image_info():
    """Test analyze() creates proper ImageInfo."""
    # Create a temporary test image
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        img = Image.new("RGB", (1920, 1080), color="red")
        img.save(tmp.name, "JPEG")
        tmp_path = Path(tmp.name)

    try:
        info = analyze(tmp_path)

        assert info.path == tmp_path
        assert info.width == 1920
        assert info.height == 1080
        assert info.format == "JPEG"
        assert info.mode == "RGB"
        assert info.file_size_bytes > 0
        assert info.orientation == ImageOrientation.LANDSCAPE
        assert info.has_transparency is False

    finally:
        tmp_path.unlink()


def test_analyze_portrait_image():
    """Test analyze() with portrait image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img = Image.new("RGB", (1080, 1920), color="blue")
        img.save(tmp.name, "PNG")
        tmp_path = Path(tmp.name)

    try:
        info = analyze(tmp_path)

        assert info.width == 1080
        assert info.height == 1920
        assert info.orientation == ImageOrientation.PORTRAIT

    finally:
        tmp_path.unlink()


def test_analyze_transparency():
    """Test analyze() detects transparency."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        img.save(tmp.name, "PNG")
        tmp_path = Path(tmp.name)

    try:
        info = analyze(tmp_path)

        assert info.has_transparency is True
        assert info.mode == "RGBA"

    finally:
        tmp_path.unlink()


def test_analyze_nonexistent_file():
    """Test analyze() raises error for nonexistent file."""
    with pytest.raises(FileNotFoundError):
        analyze(Path("/nonexistent/file.jpg"))
