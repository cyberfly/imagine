"""Image list widget with drag-and-drop support."""

from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLabel, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from imagine.gui.models.image_item import ImageItem, ProcessingStatus


# Supported image extensions
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff', '.tif'}


class ImageListWidget(QWidget):
    """
    Widget for displaying and managing list of images to optimize.

    Features:
    - Drag-and-drop support for image files
    - Add/Remove buttons
    - Status icons for each image
    - Context menu
    """

    # Signals
    items_changed = pyqtSignal()  # Emitted when items are added/removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[ImageItem] = []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 20, 0)  # Add right margin for spacing from settings panel
        layout.setSpacing(12)

        # Apply widget styles
        self.setStyleSheet("""
            QLabel {
                color: #b8b8c8;
            }
            QListWidget {
                background: rgba(30, 30, 50, 0.6);
                border: 1px solid rgba(139, 92, 246, 0.25);
                border-radius: 12px;
                padding: 8px;
                color: #e8e8e8;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background: rgba(139, 92, 246, 0.15);
            }
            QListWidget::item:selected {
                background: rgba(139, 92, 246, 0.3);
                border: 1px solid rgba(139, 92, 246, 0.5);
            }
            QPushButton {
                background: rgba(139, 92, 246, 0.2);
                color: #e8e8e8;
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
                min-height: 16px;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.3);
                border: 1px solid rgba(139, 92, 246, 0.5);
            }
            QPushButton:pressed {
                background: rgba(139, 92, 246, 0.4);
            }
        """)

        # Drop zone label
        self.drop_label = QLabel("🎨 Drop images here or click Add Images\n\nSupported formats: PNG, JPEG, WebP, GIF, BMP, TIFF")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed rgba(139, 92, 246, 0.4);
                border-radius: 16px;
                padding: 60px;
                color: #b8b8c8;
                font-size: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(139, 92, 246, 0.05),
                    stop:1 rgba(139, 92, 246, 0.1));
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.drop_label)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Images...")
        self.add_button.clicked.connect(self._add_images_dialog)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Initially hide list, show drop zone
        self._update_visibility()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any URL is an image file
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = Path(url.toLocalFile())
                    if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    paths.append(path)
                elif path.is_dir():
                    # Extract images from directory
                    for ext in SUPPORTED_EXTENSIONS:
                        paths.extend(path.glob(f"*{ext}"))

        self.add_images(paths)
        event.acceptProposedAction()

    def _add_images_dialog(self):
        """Show file dialog to add images."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.webp *.gif *.bmp *.tiff *.tif)")

        if file_dialog.exec():
            paths = [Path(p) for p in file_dialog.selectedFiles()]
            self.add_images(paths)

    def add_images(self, paths: List[Path]):
        """
        Add images to the list.

        Args:
            paths: List of image file paths
        """
        added_count = 0

        for path in paths:
            # Skip if already in list
            if any(item.path == path for item in self.items):
                continue

            # Create item
            item = ImageItem(path=path)
            self.items.append(item)

            # Add to list widget
            self._add_list_item(item)
            added_count += 1

        if added_count > 0:
            self._update_visibility()
            self.items_changed.emit()

    def _add_list_item(self, item: ImageItem):
        """Add item to list widget."""
        list_item = QListWidgetItem(self._format_item_text(item))
        list_item.setData(Qt.ItemDataRole.UserRole, item)
        self.list_widget.addItem(list_item)

    def _format_item_text(self, item: ImageItem) -> str:
        """Format display text for an item."""
        return f"{item.status_icon} {item.filename} - {item.size_display}"

    def update_item(self, path: Path, status: ProcessingStatus, result=None):
        """
        Update an item's status and result.

        Args:
            path: Path of the item to update
            status: New status
            result: OptimizationResult (optional)
        """
        # Find item
        for item in self.items:
            if item.path == path:
                item.status = status
                if result:
                    item.result = result

                # Update list widget
                for i in range(self.list_widget.count()):
                    list_item = self.list_widget.item(i)
                    item_data = list_item.data(Qt.ItemDataRole.UserRole)
                    if item_data.path == path:
                        list_item.setText(self._format_item_text(item))
                        break
                break

    def _remove_selected(self):
        """Remove selected items from list."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        for list_item in selected_items:
            item_data = list_item.data(Qt.ItemDataRole.UserRole)
            # Remove from items list
            self.items = [item for item in self.items if item.path != item_data.path]
            # Remove from list widget
            row = self.list_widget.row(list_item)
            self.list_widget.takeItem(row)

        self._update_visibility()
        self.items_changed.emit()

    def _clear_all(self):
        """Clear all items from list."""
        self.items.clear()
        self.list_widget.clear()
        self._update_visibility()
        self.items_changed.emit()

    def _show_context_menu(self, position):
        """Show context menu."""
        menu = QMenu()

        remove_action = menu.addAction("Remove Selected")
        remove_action.triggered.connect(self._remove_selected)

        clear_action = menu.addAction("Clear All")
        clear_action.triggered.connect(self._clear_all)

        menu.addSeparator()

        show_action = menu.addAction("Show in Finder")
        show_action.triggered.connect(self._show_in_finder)

        menu.exec(self.list_widget.mapToGlobal(position))

    def _show_in_finder(self):
        """Show selected files in Finder."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        import subprocess
        for list_item in selected_items:
            item_data = list_item.data(Qt.ItemDataRole.UserRole)
            subprocess.run(['open', '-R', str(item_data.path)])

    def _update_visibility(self):
        """Update visibility of drop zone vs list."""
        if len(self.items) == 0:
            self.drop_label.show()
            self.list_widget.hide()
        else:
            self.drop_label.hide()
            self.list_widget.show()

    def get_items(self) -> List[ImageItem]:
        """Get all items in the list."""
        return self.items.copy()

    def reset_all_status(self):
        """Reset all items to pending status."""
        for item in self.items:
            item.status = ProcessingStatus.PENDING
            item.result = None

        # Update all list items
        for i in range(self.list_widget.count()):
            list_item = self.list_widget.item(i)
            item_data = list_item.data(Qt.ItemDataRole.UserRole)
            list_item.setText(self._format_item_text(item_data))
