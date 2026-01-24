"""Progress widget for batch optimization."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal


class ProgressWidget(QWidget):
    """
    Widget for displaying optimization progress.

    Features:
    - Progress bar showing overall batch progress
    - Current file label
    - Cancel button
    """

    # Signals
    cancel_requested = pyqtSignal()  # Emitted when user clicks cancel

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.hide()  # Initially hidden

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(10)

        # Apply styles
        self.setStyleSheet("""
            QLabel {
                color: #c4b5fd;
                font-size: 13px;
                font-weight: 500;
            }
            QProgressBar {
                background: rgba(30, 30, 50, 0.6);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 10px;
                text-align: center;
                color: #e8e8e8;
                font-size: 12px;
                font-weight: 600;
                min-height: 24px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #6366f1);
                border-radius: 9px;
            }
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 500;
                min-height: 24px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.3);
                border: 1px solid rgba(239, 68, 68, 0.5);
            }
            QPushButton:pressed {
                background: rgba(239, 68, 68, 0.4);
            }
            QPushButton:disabled {
                background: rgba(108, 117, 125, 0.2);
                color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(108, 117, 125, 0.3);
            }
        """)

        # Current file label
        self.current_file_label = QLabel("⚡ Processing...")
        layout.addWidget(self.current_file_label)

        # Progress bar and cancel button layout
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(12)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar, stretch=1)

        self.cancel_button = QPushButton("✕ Cancel")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        progress_layout.addWidget(self.cancel_button)

        layout.addLayout(progress_layout)

    def start_progress(self, total: int):
        """
        Start progress tracking.

        Args:
            total: Total number of items to process
        """
        self.total = total
        self.current = 0
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        self.show()

    def update_progress(self, current: int, total: int):
        """
        Update progress.

        Args:
            current: Current item number (1-indexed)
            total: Total number of items
        """
        self.current = current
        self.total = total
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def update_current_file(self, filename: str):
        """
        Update current file being processed.

        Args:
            filename: Name of current file
        """
        self.current_file_label.setText(f"Processing: {filename}")

    def finish_progress(self):
        """Finish progress tracking."""
        self.current_file_label.setText("Complete!")
        self.cancel_button.setEnabled(False)

    def reset(self):
        """Reset and hide progress widget."""
        self.progress_bar.setValue(0)
        self.current_file_label.setText("Processing...")
        self.cancel_button.setEnabled(True)
        self.hide()

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_button.setEnabled(False)
        self.current_file_label.setText("Cancelling...")
        self.cancel_requested.emit()
