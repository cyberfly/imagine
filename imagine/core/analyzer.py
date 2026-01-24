"""Image analysis utilities."""

from pathlib import Path
from typing import Optional

from PIL import Image

from .config import ImageInfo, ImageOrientation


def analyze(image_path: Path) -> ImageInfo:
    """
    Analyze an image and extract its properties.

    Args:
        image_path: Path to the image file

    Returns:
        ImageInfo object with image properties

    Raises:
        FileNotFoundError: If image doesn't exist
        PIL.UnidentifiedImageError: If file is not a valid image
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Get file size
    file_size_bytes = image_path.stat().st_size

    # Open and analyze image
    with Image.open(image_path) as img:
        width, height = img.size
        format_str = img.format or "UNKNOWN"
        mode = img.mode

        # Check for transparency
        has_transparency = (
            mode in ("RGBA", "LA", "PA") or
            (mode == "P" and "transparency" in img.info)
        )

        # Get EXIF orientation if available
        exif_orientation = _get_exif_orientation(img)

        # Determine orientation (after considering EXIF rotation)
        actual_width, actual_height = _get_actual_dimensions(
            width, height, exif_orientation
        )
        orientation = _determine_orientation(actual_width, actual_height)

    return ImageInfo(
        path=image_path,
        width=actual_width,
        height=actual_height,
        format=format_str,
        mode=mode,
        file_size_bytes=file_size_bytes,
        orientation=orientation,
        has_transparency=has_transparency,
        exif_orientation=exif_orientation,
    )


def _get_exif_orientation(img: Image.Image) -> Optional[int]:
    """
    Extract EXIF orientation tag from image.

    Args:
        img: PIL Image object

    Returns:
        Orientation value (1-8) or None if not present
    """
    try:
        exif = img.getexif()
        if exif:
            # EXIF tag 274 is Orientation
            return exif.get(274)
    except (AttributeError, KeyError, TypeError):
        pass
    return None


def _get_actual_dimensions(
    width: int,
    height: int,
    exif_orientation: Optional[int]
) -> tuple[int, int]:
    """
    Get actual dimensions considering EXIF orientation.

    EXIF orientations 5, 6, 7, 8 swap width and height.

    Args:
        width: Original width
        height: Original height
        exif_orientation: EXIF orientation tag (1-8)

    Returns:
        Tuple of (actual_width, actual_height)
    """
    if exif_orientation in (5, 6, 7, 8):
        return height, width
    return width, height


def _determine_orientation(width: int, height: int) -> ImageOrientation:
    """
    Determine image orientation from dimensions.

    Args:
        width: Image width
        height: Image height

    Returns:
        ImageOrientation enum value
    """
    if width > height:
        return ImageOrientation.LANDSCAPE
    elif height > width:
        return ImageOrientation.PORTRAIT
    else:
        return ImageOrientation.SQUARE
