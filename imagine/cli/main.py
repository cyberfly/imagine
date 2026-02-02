"""CLI interface for image optimization."""

import sys
from pathlib import Path
from typing import List, Optional

import click

from imagine.core.config import ImageFormat, OptimizationConfig, WatermarkPosition
from imagine.core.optimizer import ImageOptimizer


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Imagine - Image optimization tool for web (<100KB targets)."""
    pass


@cli.command()
@click.argument("images", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "-d", "--output-dir",
    default="optimized",
    help="Output directory for optimized images",
    type=click.Path()
)
@click.option(
    "--target-size",
    default=100,
    help="Target file size in KB",
    type=int
)
@click.option(
    "--format",
    "output_format",
    default="webp",
    type=click.Choice(["webp", "jpeg", "png"], case_sensitive=False),
    help="Output image format"
)
@click.option(
    "--max-dimension",
    default=1920,
    help="Maximum width (landscape) or height (portrait) in pixels",
    type=int
)
@click.option(
    "--min-quality",
    default=60,
    help="Minimum quality before reducing dimensions",
    type=click.IntRange(1, 100)
)
@click.option(
    "--max-quality",
    default=85,
    help="Starting quality value",
    type=click.IntRange(1, 100)
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Show detailed processing information"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview without saving files"
)
@click.option(
    "--watermark",
    is_flag=True,
    help="Add watermark to optimized images"
)
@click.option(
    "--watermark-text",
    default="Imagine",
    help="Text to use for watermark",
    type=str
)
@click.option(
    "--watermark-position",
    default="bottom-right",
    type=click.Choice(["top-left", "top-right", "bottom-left", "bottom-right", "center"], case_sensitive=False),
    help="Position for watermark"
)
def optimize(
    images: tuple,
    output_dir: str,
    target_size: int,
    output_format: str,
    max_dimension: int,
    min_quality: int,
    max_quality: int,
    verbose: bool,
    dry_run: bool,
    watermark: bool,
    watermark_text: str,
    watermark_position: str
):
    """
    Optimize images for web use.

    \b
    Examples:
        imagine optimize photo.jpg
        imagine optimize photos/*.jpg photos/*.png
        imagine optimize input.jpg -d my-optimized/
        imagine optimize input.jpg --target-size 150
        imagine optimize input.jpg --format jpeg
        imagine optimize input.jpg --watermark --watermark-text "© 2026"
        imagine optimize input.jpg --watermark --watermark-position center
    """
    # Expand glob patterns and collect all image paths
    image_paths = _collect_image_paths(images)

    if not image_paths:
        click.echo("No valid images found.", err=True)
        sys.exit(1)

    # Map watermark position string to enum
    position_map = {
        "top-left": WatermarkPosition.TOP_LEFT,
        "top-right": WatermarkPosition.TOP_RIGHT,
        "bottom-left": WatermarkPosition.BOTTOM_LEFT,
        "bottom-right": WatermarkPosition.BOTTOM_RIGHT,
        "center": WatermarkPosition.CENTER,
    }

    # Create configuration
    config = OptimizationConfig(
        target_size_kb=target_size,
        output_format=ImageFormat(output_format.lower()),
        output_dir=output_dir,
        max_dimension=max_dimension,
        min_quality=min_quality,
        max_quality=max_quality,
        watermark=watermark,
        watermark_text=watermark_text,
        watermark_position=position_map[watermark_position.lower()],
    )

    # Show configuration if verbose
    if verbose:
        click.echo(f"Configuration:")
        click.echo(f"  Target size: {config.target_size_kb}KB")
        click.echo(f"  Output format: {config.output_format.value}")
        click.echo(f"  Max dimension: {config.max_dimension}px")
        click.echo(f"  Quality range: {config.min_quality}-{config.max_quality}")
        click.echo(f"  Output directory: {config.output_dir}")
        if config.watermark:
            click.echo(f"  Watermark: {config.watermark_text} ({config.watermark_position.value})")
        click.echo()

    if dry_run:
        click.echo("[DRY RUN] Would optimize the following images:")
        for path in image_paths:
            click.echo(f"  - {path}")
        click.echo()
        click.echo(f"Output directory: {output_dir}")
        return

    # Create optimizer
    optimizer = ImageOptimizer(config)

    # Show progress
    click.echo(f"Optimizing {len(image_paths)} image(s)...")

    # Process images with progress bar
    results = []
    with click.progressbar(
        image_paths,
        label="Processing",
        item_show_func=lambda p: p.name if p else ""
    ) as bar:
        for image_path in bar:
            result = optimizer.optimize(image_path)
            results.append(result)

            if verbose and result.success:
                click.echo(f"\n  {result}")

    # Print summary
    click.echo()
    _print_summary(results, verbose)


def _collect_image_paths(patterns: tuple) -> List[Path]:
    """
    Collect all valid image paths from patterns.

    Args:
        patterns: Tuple of file paths or glob patterns

    Returns:
        List of Path objects
    """
    image_paths = []
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

    for pattern in patterns:
        path = Path(pattern)

        if path.is_file():
            if path.suffix.lower() in valid_extensions:
                image_paths.append(path)
        elif path.is_dir():
            # If directory given, find all images
            for ext in valid_extensions:
                image_paths.extend(path.glob(f"*{ext}"))
                image_paths.extend(path.glob(f"*{ext.upper()}"))

    return sorted(set(image_paths))


def _print_summary(results: list, verbose: bool):
    """
    Print optimization summary.

    Args:
        results: List of OptimizationResult objects
        verbose: Whether to show detailed information
    """
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    click.echo("=" * 70)
    click.echo(f"SUMMARY: {len(successful)}/{len(results)} images optimized successfully")
    click.echo("=" * 70)

    if successful:
        # Calculate statistics
        total_original = sum(r.original_size_bytes for r in successful)
        total_optimized = sum(r.optimized_size_bytes for r in successful)
        total_saved = total_original - total_optimized
        avg_reduction = (total_saved / total_original * 100) if total_original > 0 else 0

        click.echo()
        click.echo("Statistics:")
        click.echo(f"  Original total:   {total_original / 1024 / 1024:.2f} MB")
        click.echo(f"  Optimized total:  {total_optimized / 1024 / 1024:.2f} MB")
        click.echo(f"  Space saved:      {total_saved / 1024 / 1024:.2f} MB ({avg_reduction:.1f}%)")

        # Show individual results
        if not verbose:
            click.echo()
            click.echo("Results:")
            for result in successful:
                status = "✓" if result.optimized_size_kb <= 100 else "⚠"
                click.echo(
                    f"  {status} {result.input_path.name}: "
                    f"{result.original_size_kb:.1f}KB → {result.optimized_size_kb:.1f}KB "
                    f"({result.size_reduction_percent:.1f}% reduction)"
                )

        # Warn about images still over target
        over_target = [r for r in successful if r.optimized_size_kb > 100]
        if over_target:
            click.echo()
            click.echo(f"⚠ Warning: {len(over_target)} image(s) still over 100KB target:")
            for result in over_target:
                click.echo(f"  - {result.input_path.name}: {result.optimized_size_kb:.1f}KB")

    if failed:
        click.echo()
        click.echo(f"Failed ({len(failed)}):")
        for result in failed:
            click.echo(f"  ❌ {result.input_path.name}: {result.error_message}")

    click.echo()


@cli.command()
@click.argument("image", type=click.Path(exists=True))
def info(image: str):
    """Show information about an image."""
    from imagine.core.analyzer import analyze

    try:
        image_path = Path(image)
        image_info = analyze(image_path)

        click.echo(f"Image: {image_info.path.name}")
        click.echo(f"  Dimensions:   {image_info.width}x{image_info.height}")
        click.echo(f"  Format:       {image_info.format}")
        click.echo(f"  Mode:         {image_info.mode}")
        click.echo(f"  Size:         {image_info.file_size_kb:.2f} KB")
        click.echo(f"  Orientation:  {image_info.orientation.value}")
        click.echo(f"  Transparency: {'Yes' if image_info.has_transparency else 'No'}")
        if image_info.exif_orientation:
            click.echo(f"  EXIF Orient:  {image_info.exif_orientation}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
