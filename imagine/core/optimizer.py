"""Main image optimizer orchestration."""

from pathlib import Path
from typing import Callable, List, Optional

from .analyzer import analyze
from .config import ImageFormat, OptimizationConfig, OptimizationResult
from .processor import save_image
from .strategy import AdaptiveStrategy


class ImageOptimizer:
    """
    Main image optimizer class.

    This is the primary interface for image optimization.
    UI-agnostic - can be used by CLI, GUI, or any other interface.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize optimizer with configuration.

        Args:
            config: OptimizationConfig object (uses defaults if None)
        """
        self.config = config or OptimizationConfig()
        self.strategy = AdaptiveStrategy(self.config)

    def optimize(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> OptimizationResult:
        """
        Optimize a single image.

        Args:
            input_path: Path to input image
            output_path: Path for output (auto-generated if None)
            callback: Optional callback(current, total) for progress

        Returns:
            OptimizationResult object
        """
        try:
            # Analyze input image
            image_info = analyze(input_path)

            # Check if already under target size
            if image_info.file_size_kb <= self.config.target_size_kb:
                # Already optimized, but still process to convert format if needed
                pass

            # Determine output path
            if output_path is None:
                output_path = self._generate_output_path(input_path)

            # Execute optimization strategy
            (
                image_bytes,
                final_width,
                final_height,
                final_quality,
                iterations
            ) = self.strategy.execute(image_info)

            # Save optimized image
            save_image(image_bytes, output_path)

            # Create result
            result = OptimizationResult(
                input_path=input_path,
                output_path=output_path,
                success=True,
                original_size_bytes=image_info.file_size_bytes,
                original_width=image_info.width,
                original_height=image_info.height,
                original_format=image_info.format,
                optimized_size_bytes=len(image_bytes),
                optimized_width=final_width,
                optimized_height=final_height,
                optimized_format=self.config.output_format.value,
                final_quality=final_quality,
                iterations=iterations,
            )

            if callback:
                callback(1, 1)

            return result

        except Exception as e:
            # Return failure result
            return OptimizationResult(
                input_path=input_path,
                output_path=output_path or Path("unknown"),
                success=False,
                original_size_bytes=0,
                original_width=0,
                original_height=0,
                original_format="unknown",
                optimized_size_bytes=0,
                optimized_width=0,
                optimized_height=0,
                optimized_format="unknown",
                final_quality=0,
                iterations=0,
                error_message=str(e),
            )

    def optimize_batch(
        self,
        input_paths: List[Path],
        output_dir: Optional[Path] = None,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> List[OptimizationResult]:
        """
        Optimize multiple images.

        Args:
            input_paths: List of input image paths
            output_dir: Directory for outputs (uses config.output_dir if None)
            callback: Optional callback(current, total) for progress

        Returns:
            List of OptimizationResult objects
        """
        if output_dir is None:
            output_dir = Path(self.config.output_dir)

        results = []
        total = len(input_paths)

        for idx, input_path in enumerate(input_paths, 1):
            # Generate output path
            output_path = output_dir / self._generate_output_filename(input_path)

            # Optimize
            result = self.optimize(input_path, output_path)
            results.append(result)

            # Progress callback
            if callback:
                callback(idx, total)

        return results

    def _generate_output_path(self, input_path: Path) -> Path:
        """
        Generate output path based on input path.

        Args:
            input_path: Input image path

        Returns:
            Output path in configured output directory
        """
        output_dir = Path(self.config.output_dir)
        filename = self._generate_output_filename(input_path)
        return output_dir / filename

    def _generate_output_filename(self, input_path: Path) -> str:
        """
        Generate output filename with correct extension.

        Args:
            input_path: Input image path

        Returns:
            Output filename string
        """
        stem = input_path.stem
        ext = self._get_extension_for_format(self.config.output_format)
        return f"{stem}.{ext}"

    def _get_extension_for_format(self, format: ImageFormat) -> str:
        """
        Get file extension for format.

        Args:
            format: ImageFormat enum

        Returns:
            File extension (without dot)
        """
        return format.value


def optimize_single(
    input_path: str,
    output_path: Optional[str] = None,
    config: Optional[OptimizationConfig] = None
) -> OptimizationResult:
    """
    Convenience function to optimize a single image.

    Args:
        input_path: Path to input image
        output_path: Path for output (auto-generated if None)
        config: OptimizationConfig object (uses defaults if None)

    Returns:
        OptimizationResult object
    """
    optimizer = ImageOptimizer(config)
    return optimizer.optimize(
        Path(input_path),
        Path(output_path) if output_path else None
    )


def optimize_batch(
    input_paths: List[str],
    output_dir: Optional[str] = None,
    config: Optional[OptimizationConfig] = None,
    callback: Optional[Callable[[int, int], None]] = None
) -> List[OptimizationResult]:
    """
    Convenience function to optimize multiple images.

    Args:
        input_paths: List of input image paths
        output_dir: Directory for outputs (uses config.output_dir if None)
        config: OptimizationConfig object (uses defaults if None)
        callback: Optional callback(current, total) for progress

    Returns:
        List of OptimizationResult objects
    """
    optimizer = ImageOptimizer(config)
    return optimizer.optimize_batch(
        [Path(p) for p in input_paths],
        Path(output_dir) if output_dir else None,
        callback
    )
