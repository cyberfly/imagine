"""Adaptive optimization strategy."""

from typing import Tuple

from PIL import Image

from .config import ImageInfo, OptimizationConfig
from .processor import (
    compress_image,
    load_and_prepare_image,
    resize,
    scale_dimensions,
)


class AdaptiveStrategy:
    """
    Adaptive multi-pass optimization strategy.

    Algorithm:
    1. Start with initial resize to max_dimension
    2. Try compression with decreasing quality
    3. If still too large, reduce dimensions and retry
    4. Continue until target size reached or limits hit
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize strategy with configuration.

        Args:
            config: OptimizationConfig object
        """
        self.config = config

    def execute(
        self,
        image_info: ImageInfo
    ) -> Tuple[bytes, int, int, int, int]:
        """
        Execute optimization strategy.

        Returns:
            Tuple of (image_bytes, final_width, final_height, final_quality, iterations)

        Raises:
            RuntimeError: If optimization fails to meet target
        """
        # Load and prepare image
        img = load_and_prepare_image(image_info)

        # Phase 1: Initial resize to max_dimension
        img = resize(
            img,
            self.config.max_dimension,
            image_info.orientation
        )

        # Track iterations
        iteration = 0
        current_quality = self.config.max_quality
        dimension_scale = 1.0

        target_bytes = self.config.target_size_kb * 1024

        while iteration < self.config.max_iterations:
            iteration += 1

            # Try compression at current settings
            image_bytes = compress_image(
                img,
                self.config.output_format,
                current_quality,
                image_info.has_transparency
            )

            current_size = len(image_bytes)

            # Check if we've met the target
            if current_size <= target_bytes:
                width, height = img.size
                return image_bytes, width, height, current_quality, iteration

            # Phase 2: Reduce quality
            if current_quality > self.config.min_quality:
                current_quality = max(
                    self.config.min_quality,
                    current_quality - self.config.quality_step
                )
                continue

            # Phase 3: Reduce dimensions
            # Reset quality for next dimension attempt
            current_quality = self.config.max_quality

            # Calculate new dimension scale
            dimension_scale -= self.config.dimension_reduction_step

            # Check if we've hit minimum dimensions
            if dimension_scale < self.config.min_dimension_scale:
                # Return best effort
                width, height = img.size
                return image_bytes, width, height, self.config.min_quality, iteration

            # Apply dimension reduction
            img = scale_dimensions(
                load_and_prepare_image(image_info),  # Start from original
                dimension_scale
            )

        # Max iterations reached - return best effort
        width, height = img.size
        return image_bytes, width, height, current_quality, iteration


class FastStrategy:
    """
    Fast single-pass optimization strategy.

    Good for batch processing where speed is more important than
    achieving exact target size.
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize strategy with configuration.

        Args:
            config: OptimizationConfig object
        """
        self.config = config

    def execute(
        self,
        image_info: ImageInfo
    ) -> Tuple[bytes, int, int, int, int]:
        """
        Execute fast optimization.

        Returns:
            Tuple of (image_bytes, final_width, final_height, final_quality, iterations)
        """
        # Load and prepare image
        img = load_and_prepare_image(image_info)

        # Resize to max_dimension
        img = resize(
            img,
            self.config.max_dimension,
            image_info.orientation
        )

        # Use fixed quality of 80
        quality = 80

        # Compress
        image_bytes = compress_image(
            img,
            self.config.output_format,
            quality,
            image_info.has_transparency
        )

        width, height = img.size
        return image_bytes, width, height, quality, 1
