"""Low-level image processing operations using Pillow."""

import io
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps

from .config import ImageFormat, ImageInfo, ImageOrientation


def load_and_prepare_image(image_info: ImageInfo) -> Image.Image:
    """
    Load an image and prepare it for processing.

    Handles EXIF orientation and converts to RGB/RGBA as needed.

    Args:
        image_info: ImageInfo object

    Returns:
        Prepared PIL Image object
    """
    img = Image.open(image_info.path)

    # Apply EXIF orientation (auto-rotate based on camera orientation)
    img = ImageOps.exif_transpose(img)

    # Convert mode if needed
    if image_info.has_transparency:
        # Keep transparency for WebP/PNG
        if img.mode not in ("RGBA", "LA"):
            img = img.convert("RGBA")
    else:
        # Convert to RGB for better compression
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

    return img


def resize(
    img: Image.Image,
    max_dimension: int,
    orientation: ImageOrientation
) -> Image.Image:
    """
    Resize image maintaining aspect ratio.

    Args:
        img: PIL Image object
        max_dimension: Maximum width (landscape) or height (portrait)
        orientation: Image orientation

    Returns:
        Resized PIL Image object
    """
    width, height = img.size

    # Calculate new dimensions
    if orientation == ImageOrientation.LANDSCAPE:
        if width > max_dimension:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            return img  # No resize needed
    elif orientation == ImageOrientation.PORTRAIT:
        if height > max_dimension:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        else:
            return img  # No resize needed
    else:  # SQUARE
        if width > max_dimension or height > max_dimension:
            new_width = new_height = max_dimension
        else:
            return img  # No resize needed

    # Use LANCZOS resampling for high-quality downscaling
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def scale_dimensions(
    img: Image.Image,
    scale_factor: float
) -> Image.Image:
    """
    Scale image dimensions by a factor.

    Args:
        img: PIL Image object
        scale_factor: Factor to scale by (e.g., 0.9 for 90% of original)

    Returns:
        Scaled PIL Image object
    """
    width, height = img.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Ensure minimum size
    new_width = max(new_width, 100)
    new_height = max(new_height, 100)

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def compress_to_webp(
    img: Image.Image,
    quality: int,
    has_transparency: bool
) -> bytes:
    """
    Compress image to WebP format.

    Args:
        img: PIL Image object
        quality: Quality setting (0-100)
        has_transparency: Whether to preserve transparency

    Returns:
        Compressed image as bytes
    """
    output = io.BytesIO()

    # WebP options
    save_kwargs = {
        "format": "WEBP",
        "quality": quality,
        "method": 6,  # Maximum compression effort
    }

    # Handle transparency
    if has_transparency and img.mode in ("RGBA", "LA"):
        save_kwargs["lossless"] = False  # Use lossy with alpha

    img.save(output, **save_kwargs)
    return output.getvalue()


def compress_to_jpeg(
    img: Image.Image,
    quality: int
) -> bytes:
    """
    Compress image to JPEG format.

    Args:
        img: PIL Image object
        quality: Quality setting (0-100)

    Returns:
        Compressed image as bytes
    """
    output = io.BytesIO()

    # Convert to RGB if needed (JPEG doesn't support transparency)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    img.save(
        output,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
    )
    return output.getvalue()


def compress_to_png(
    img: Image.Image,
) -> bytes:
    """
    Compress image to PNG format.

    PNG uses lossless compression, so no quality parameter.

    Args:
        img: PIL Image object

    Returns:
        Compressed image as bytes
    """
    output = io.BytesIO()

    img.save(
        output,
        format="PNG",
        optimize=True,
    )
    return output.getvalue()


def compress_image(
    img: Image.Image,
    output_format: ImageFormat,
    quality: int,
    has_transparency: bool
) -> bytes:
    """
    Compress image to specified format.

    Args:
        img: PIL Image object
        output_format: Target format
        quality: Quality setting (0-100, ignored for PNG)
        has_transparency: Whether image has transparency

    Returns:
        Compressed image as bytes
    """
    if output_format == ImageFormat.WEBP:
        return compress_to_webp(img, quality, has_transparency)
    elif output_format == ImageFormat.JPEG:
        return compress_to_jpeg(img, quality)
    elif output_format == ImageFormat.PNG:
        return compress_to_png(img)
    else:
        raise ValueError(f"Unsupported format: {output_format}")


def save_image(
    image_bytes: bytes,
    output_path: Path
) -> None:
    """
    Save compressed image bytes to file.

    Args:
        image_bytes: Compressed image data
        output_path: Path to save the image
    """
    # Create parent directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(image_bytes)
