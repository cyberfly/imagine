"""Theme support for GUI."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def apply_theme(app: QApplication) -> None:
    """
    Apply modern theme to the application.

    Uses Fusion style for modern, cross-platform look.
    Respects system theme (light/dark mode).

    Args:
        app: QApplication instance
    """
    # Use Fusion style for modern look
    app.setStyle("Fusion")

    # The Fusion style automatically adapts to system theme on macOS
    # No need for custom palette unless we want specific colors


def get_status_colors() -> dict:
    """
    Get color scheme for status indicators.

    Returns:
        Dictionary mapping status to color hex codes
    """
    return {
        'pending': '#6c757d',    # Gray
        'processing': '#0d6efd',  # Blue
        'success': '#198754',     # Green
        'error': '#dc3545',       # Red
    }
