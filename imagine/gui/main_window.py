"""Main window for Imagine GUI."""

import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QStatusBar, QMessageBox,
    QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QKeySequence

from imagine.gui.widgets.image_list import ImageListWidget
from imagine.gui.widgets.settings import SettingsWidget
from imagine.gui.widgets.progress import ProgressWidget
from imagine.gui.workers.optimizer_worker import OptimizerWorker
from imagine.gui.models.image_item import ProcessingStatus
from imagine.gui.utils.formatters import format_file_size


class MainWindow(QMainWindow):
    """
    Main window for Imagine image optimizer.

    Features:
    - Two-panel layout (image list + settings)
    - Menu bar with File, Edit, Help
    - Status bar
    - Progress tracking
    - Batch optimization
    """

    def __init__(self):
        super().__init__()
        self.settings = QSettings("Imagine", "Imagine")
        self.worker = None
        self._init_ui()
        self._load_window_settings()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Imagine - Image Optimizer")
        self.setMinimumSize(1000, 700)

        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
            }
            QWidget {
                font-family: '.AppleSystemUIFont', 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
                color: #e8e8e8;
            }
            QMenuBar {
                background-color: rgba(30, 30, 50, 0.8);
                color: #e8e8e8;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: rgba(139, 92, 246, 0.3);
            }
            QMenu {
                background-color: rgba(30, 30, 50, 0.95);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(139, 92, 246, 0.4);
            }
            QStatusBar {
                background-color: rgba(30, 30, 50, 0.6);
                color: #a8a8b8;
                border-top: 1px solid rgba(139, 92, 246, 0.2);
            }
        """)

        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Splitter for two-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Image list
        self.image_list = ImageListWidget()
        self.image_list.items_changed.connect(self._on_items_changed)
        splitter.addWidget(self.image_list)

        # Right panel - Settings
        self.settings_widget = SettingsWidget()
        splitter.addWidget(self.settings_widget)

        # Set initial splitter sizes (60% left, 40% right)
        splitter.setSizes([540, 360])

        main_layout.addWidget(splitter)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Optimization")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._start_optimization)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.start_button)

        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self._open_output_folder)
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5c636a;
            }
        """)
        button_layout.addWidget(self.open_folder_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Progress widget
        self.progress_widget = ProgressWidget()
        self.progress_widget.cancel_requested.connect(self._cancel_optimization)
        main_layout.addWidget(self.progress_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Create menu bar (after widgets are initialized)
        self._create_menu_bar()

    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Add Images...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.image_list._add_images_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        clear_action = QAction("Clear All Images", self)
        clear_action.triggered.connect(self.image_list._clear_all)
        edit_menu.addAction(clear_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About Imagine", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _on_items_changed(self):
        """Handle image list items changed."""
        item_count = len(self.image_list.get_items())
        self.start_button.setEnabled(item_count > 0)

        if item_count > 0:
            self.status_bar.showMessage(f"{item_count} image(s) ready")
        else:
            self.status_bar.showMessage("Ready")

    def _open_output_folder(self):
        """Open the output directory in Finder."""
        config = self.settings_widget.get_config()
        output_dir = Path(config.output_dir)

        # Create directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Open in Finder
        subprocess.run(['open', str(output_dir)])
        self.status_bar.showMessage(f"Opened {output_dir}")

    def _start_optimization(self):
        """Start batch optimization."""
        items = self.image_list.get_items()
        if not items:
            return

        # Validate output directory
        config = self.settings_widget.get_config()
        output_dir = Path(config.output_dir)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot create output directory: {e}"
            )
            return

        # Check if output directory is writable
        if not output_dir.is_dir() or not output_dir.exists():
            QMessageBox.critical(
                self,
                "Error",
                f"Output directory is not valid: {output_dir}"
            )
            return

        # Reset all items to pending
        self.image_list.reset_all_status()

        # Disable controls
        self.start_button.setEnabled(False)
        self.image_list.setEnabled(False)
        self.settings_widget.setEnabled(False)

        # Start progress
        self.progress_widget.start_progress(len(items))

        # Create and start worker
        self.worker = OptimizerWorker(items, config)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.image_started.connect(self._on_image_started)
        self.worker.image_completed.connect(self._on_image_completed)
        self.worker.batch_completed.connect(self._on_batch_completed)
        self.worker.error_occurred.connect(self._on_error_occurred)
        self.worker.start()

    def _cancel_optimization(self):
        """Cancel ongoing optimization."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_bar.showMessage("Cancelling...")

    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update."""
        self.progress_widget.update_progress(current, total)

    def _on_image_started(self, filename: str):
        """Handle image started."""
        self.progress_widget.update_current_file(filename)
        self.status_bar.showMessage(f"Processing {filename}...")

        # Update item status to processing
        for item in self.image_list.get_items():
            if item.filename == filename:
                self.image_list.update_item(
                    item.path,
                    ProcessingStatus.PROCESSING
                )
                break

    def _on_image_completed(self, result):
        """Handle image completion."""
        # Update item
        if result.success:
            self.image_list.update_item(
                result.input_path,
                ProcessingStatus.SUCCESS,
                result
            )
        else:
            self.image_list.update_item(
                result.input_path,
                ProcessingStatus.ERROR,
                result
            )

    def _on_batch_completed(self, results):
        """Handle batch completion."""
        # Calculate statistics
        success_count = sum(1 for r in results if r.success)
        total_original = sum(r.original_size_bytes for r in results if r.success)
        total_optimized = sum(r.optimized_size_bytes for r in results if r.success)
        total_saved = total_original - total_optimized

        # Finish progress
        self.progress_widget.finish_progress()

        # Re-enable controls
        self.start_button.setEnabled(True)
        self.image_list.setEnabled(True)
        self.settings_widget.setEnabled(True)

        # Show completion message
        if success_count > 0:
            saved_str = format_file_size(total_saved)
            percent = (total_saved / total_original * 100) if total_original > 0 else 0
            message = (
                f"Optimized {success_count} of {len(results)} image(s)\n"
                f"Saved {saved_str} ({percent:.1f}% reduction)"
            )
            self.status_bar.showMessage(f"Complete! Saved {saved_str}")

            QMessageBox.information(
                self,
                "Optimization Complete",
                message
            )
        else:
            self.status_bar.showMessage("Optimization failed")
            QMessageBox.warning(
                self,
                "Optimization Failed",
                "No images were successfully optimized."
            )

        # Reset progress widget after a delay
        self.progress_widget.reset()

    def _on_error_occurred(self, filename: str, error_message: str):
        """Handle error."""
        # Error is already reflected in the list item
        # Just log to status bar
        self.status_bar.showMessage(f"Error processing {filename}")

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Imagine",
            "<h2>Imagine Image Optimizer</h2>"
            "<p>Version 0.1.0</p>"
            "<p>Optimize images for the web with focus on &lt;100KB targets.</p>"
            "<p>Built with PyQt6 and Pillow.</p>"
        )

    def _save_window_settings(self):
        """Save window position and size."""
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())

    def _load_window_settings(self):
        """Load window position and size."""
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value("window_state")
        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any running worker
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()

        # Save window settings
        self._save_window_settings()

        event.accept()
