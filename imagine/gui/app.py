"""Application entry point for Imagine GUI."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from imagine.gui.main_window import MainWindow
from imagine.gui.utils.theme import apply_theme


def main():
    """
    Main entry point for Imagine GUI application.

    Initializes QApplication with high-DPI support and launches MainWindow.
    """
    # Enable high-DPI scaling for Retina displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)

    # Set application metadata for settings persistence
    app.setOrganizationName("Imagine")
    app.setApplicationName("Imagine")
    app.setApplicationDisplayName("Imagine")

    # Apply theme
    apply_theme(app)

    # Set application icon
    icon_path = Path(__file__).parent.parent.parent / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Enter event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
