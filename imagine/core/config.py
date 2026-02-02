"""Configuration dataclasses for image optimization."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class ImageFormat(Enum):
    """Supported output image formats."""
    WEBP = "webp"
    JPEG = "jpeg"
    PNG = "png"
    AVIF = "avif"


class ImageOrientation(Enum):
    """Image orientation types."""
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class WatermarkPosition(Enum):
    """Watermark position options."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


@dataclass
class OptimizationConfig:
    """Configuration for image optimization."""

    # Target file size in KB
    target_size_kb: int = 100

    # Output format
    output_format: ImageFormat = ImageFormat.WEBP

    # Quality settings
    min_quality: int = 60  # Minimum quality before we start reducing dimensions
    max_quality: int = 85  # Starting quality
    quality_step: int = 5  # How much to reduce quality each iteration

    # Dimension settings
    max_dimension: int = 1920  # Max width for landscape, max height for portrait
    min_dimension_scale: float = 0.5  # Don't reduce dimensions below 50% of original
    dimension_reduction_step: float = 0.1  # Reduce by 10% each iteration

    # Output settings
    preserve_originals: bool = True
    output_dir: str = "optimized"
    watermark: bool = False  # Add watermark to optimized images
    watermark_text: str = "Imagine"  # Text to use for watermark
    watermark_position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT  # Watermark position

    # Performance
    max_iterations: int = 20  # Prevent infinite loops


@dataclass
class ImageInfo:
    """Information about an image."""

    path: Path
    width: int
    height: int
    format: str
    mode: str  # RGB, RGBA, etc.
    file_size_bytes: int
    orientation: ImageOrientation
    has_transparency: bool
    exif_orientation: Optional[int] = None

    @property
    def file_size_kb(self) -> float:
        """File size in KB."""
        return self.file_size_bytes / 1024

    @property
    def aspect_ratio(self) -> float:
        """Width / height ratio."""
        return self.width / self.height if self.height > 0 else 1.0

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"{self.path.name} - {self.width}x{self.height} "
            f"{self.format} ({self.file_size_kb:.1f}KB) "
            f"[{self.orientation.value}]"
        )


@dataclass
class OptimizationResult:
    """Result of image optimization."""

    input_path: Path
    output_path: Path
    success: bool

    # Original image info
    original_size_bytes: int
    original_width: int
    original_height: int
    original_format: str

    # Optimized image info
    optimized_size_bytes: int
    optimized_width: int
    optimized_height: int
    optimized_format: str
    final_quality: int

    # Processing info
    iterations: int
    error_message: Optional[str] = None

    @property
    def original_size_kb(self) -> float:
        """Original file size in KB."""
        return self.original_size_bytes / 1024

    @property
    def optimized_size_kb(self) -> float:
        """Optimized file size in KB."""
        return self.optimized_size_bytes / 1024

    @property
    def size_reduction_percent(self) -> float:
        """Percentage reduction in file size."""
        if self.original_size_bytes == 0:
            return 0.0
        reduction = self.original_size_bytes - self.optimized_size_bytes
        return (reduction / self.original_size_bytes) * 100

    @property
    def dimension_scale(self) -> float:
        """Scale factor for dimensions (0-1)."""
        original_pixels = self.original_width * self.original_height
        optimized_pixels = self.optimized_width * self.optimized_height
        if original_pixels == 0:
            return 1.0
        return (optimized_pixels / original_pixels) ** 0.5

    def __str__(self) -> str:
        """Human-readable representation."""
        if not self.success:
            return f"❌ {self.input_path.name}: {self.error_message}"

        return (
            f"✓ {self.input_path.name}: "
            f"{self.original_size_kb:.1f}KB → {self.optimized_size_kb:.1f}KB "
            f"({self.size_reduction_percent:.1f}% reduction) "
            f"[{self.optimized_width}x{self.optimized_height}, q={self.final_quality}]"
        )
