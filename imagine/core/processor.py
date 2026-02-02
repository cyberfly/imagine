"""Low-level image processing operations using Pillow."""

import io
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps, ImageDraw, ImageFont

# Register HEIF plugin for AVIF support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # AVIF support optional

from .config import ImageFormat, ImageInfo, ImageOrientation, WatermarkPosition


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


def add_watermark(
    img: Image.Image,
    text: str = "Imagine",
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
    font_size: int = 0,
    transparent_bg: bool = False
) -> Image.Image:
    """
    Add a watermark to the image.

    Adds custom text at specified position with optional background.

    Args:
        img: PIL Image object
        text: Watermark text to display
        position: Position for the watermark
        font_size: Font size in pixels (0 = auto-calculate based on image size)
        transparent_bg: If True, no background rectangle is drawn

    Returns:
        Image with watermark applied
    """
    # Create a copy to avoid modifying the original
    watermarked = img.copy()

    # Get image dimensions
    width, height = watermarked.size

    # Calculate font size based on image size if not specified (roughly 2% of image width)
    if font_size == 0:
        font_size = max(12, int(width * 0.02))

    # Try to use a better font, fall back to default if not available
    try:
        # Try common system fonts
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except Exception:
            # Fall back to default font
            font = ImageFont.load_default()

    # Watermark text
    watermark_text = text

    # Create a drawing context
    draw = ImageDraw.Draw(watermarked, "RGBA")

    # Get text bounding box
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate padding
    padding = max(10, int(width * 0.01))

    # Calculate position based on selection
    if position == WatermarkPosition.TOP_LEFT:
        x = padding
        y = padding
    elif position == WatermarkPosition.TOP_RIGHT:
        x = width - text_width - padding * 2
        y = padding
    elif position == WatermarkPosition.BOTTOM_LEFT:
        x = padding
        y = height - text_height - padding * 2
    elif position == WatermarkPosition.BOTTOM_RIGHT:
        x = width - text_width - padding * 2
        y = height - text_height - padding * 2
    elif position == WatermarkPosition.CENTER:
        x = (width - text_width) // 2
        y = (height - text_height) // 2
    else:
        # Default to bottom-right
        x = width - text_width - padding * 2
        y = height - text_height - padding * 2

    # Draw semi-transparent background rectangle (if not transparent)
    if not transparent_bg:
        bg_rect = [
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding
        ]
        draw.rectangle(bg_rect, fill=(0, 0, 0, 128))

    # Draw text (white with slight transparency)
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 230))

    return watermarked


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


def compress_to_avif(
    img: Image.Image,
    quality: int,
    has_transparency: bool
) -> bytes:
    """
    Compress image to AVIF format.

    Args:
        img: PIL Image object
        quality: Quality setting (0-100)
        has_transparency: Whether to preserve transparency

    Returns:
        Compressed image as bytes
    """
    output = io.BytesIO()

    # AVIF options
    save_kwargs = {
        "format": "AVIF",
        "quality": quality,
    }

    # Handle transparency
    if has_transparency and img.mode in ("RGBA", "LA"):
        # AVIF supports transparency
        pass
    elif img.mode not in ("RGB", "L"):
        # Convert to RGB if no transparency needed
        img = img.convert("RGB")

    img.save(output, **save_kwargs)
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
    elif output_format == ImageFormat.AVIF:
        return compress_to_avif(img, quality, has_transparency)
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
