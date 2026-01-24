"""Formatting utilities for GUI display."""


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string like "1.2 MB" or "500 KB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_percent(value: float) -> str:
    """
    Format percentage value.

    Args:
        value: Percentage value (0-100)

    Returns:
        Formatted string like "92.5%"
    """
    return f"{value:.1f}%"


def format_dimensions(width: int, height: int) -> str:
    """
    Format image dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Formatted string like "1920×1080"
    """
    return f"{width}×{height}"
