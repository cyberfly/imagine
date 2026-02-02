"""Settings widget with persistence."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QSpinBox, QComboBox, QLineEdit, QPushButton,
    QHBoxLayout, QFileDialog, QLabel, QAbstractSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal

from imagine.core.config import OptimizationConfig, ImageFormat, WatermarkPosition


class SettingsWidget(QWidget):
    """
    Widget for optimization settings.

    Features:
    - Form controls for all optimization parameters
    - QSettings persistence (auto-save on change)
    - get_config() method to convert UI state to OptimizationConfig
    """

    # Signals
    settings_changed = pyqtSignal()  # Emitted when any setting changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("Imagine", "Imagine")
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 0, 0, 0)  # Add left margin for spacing from image list panel
        layout.setSpacing(16)

        # Get resource paths for arrow icons
        resources_dir = Path(__file__).parent.parent / "resources"
        arrow_up = (resources_dir / "arrow-up.svg").as_posix()
        arrow_down = (resources_dir / "arrow-down.svg").as_posix()

        # Apply widget styles (use .format() for path substitution)
        stylesheet = """
            QGroupBox {
                background: rgba(30, 30, 50, 0.6);
                border: 1px solid rgba(139, 92, 246, 0.25);
                border-radius: 12px;
                padding: 20px;
                margin-top: 12px;
                font-size: 15px;
                font-weight: 600;
                color: #e8e8e8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background: rgba(139, 92, 246, 0.2);
                border-radius: 6px;
                color: #c4b5fd;
            }
            QLabel {
                color: #b8b8c8;
                font-size: 13px;
            }
            QSpinBox, QComboBox, QLineEdit {
                background: rgba(15, 15, 35, 0.6);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                padding: 8px 12px;
                color: #e8e8e8;
                font-size: 13px;
                min-height: 20px;
            }
            QSpinBox:hover, QComboBox:hover, QLineEdit:hover {
                border: 1px solid rgba(139, 92, 246, 0.5);
                background: rgba(15, 15, 35, 0.8);
            }
            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 1px solid rgba(139, 92, 246, 0.8);
                background: rgba(15, 15, 35, 0.9);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(139, 92, 246, 0.2);
                border: none;
                border-radius: 4px;
                width: 20px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: rgba(139, 92, 246, 0.4);
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background: rgba(139, 92, 246, 0.6);
            }
            QSpinBox::up-arrow {
                image: url("ARROW_UP_PATH");
                width: 10px;
                height: 6px;
            }
            QSpinBox::down-arrow {
                image: url("ARROW_DOWN_PATH");
                width: 10px;
                height: 6px;
            }
            QComboBox::drop-down {
                border: none;
                background: rgba(139, 92, 246, 0.2);
                border-radius: 4px;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: url("ARROW_DOWN_PATH");
                width: 10px;
                height: 6px;
            }
            QComboBox QAbstractItemView {
                background: rgba(30, 30, 50, 0.95);
                border: 1px solid rgba(139, 92, 246, 0.4);
                border-radius: 8px;
                selection-background-color: rgba(139, 92, 246, 0.4);
                color: #e8e8e8;
                padding: 4px;
            }
            QPushButton {
                background: rgba(139, 92, 246, 0.2);
                color: #e8e8e8;
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.3);
                border: 1px solid rgba(139, 92, 246, 0.5);
            }
            QPushButton:pressed {
                background: rgba(139, 92, 246, 0.4);
            }
            QCheckBox {
                color: #e8e8e8;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 4px;
                background: rgba(15, 15, 35, 0.6);
            }
            QCheckBox::indicator:hover {
                border: 1px solid rgba(139, 92, 246, 0.5);
                background: rgba(15, 15, 35, 0.8);
            }
            QCheckBox::indicator:checked {
                background: rgba(139, 92, 246, 0.6);
                border: 1px solid rgba(139, 92, 246, 0.8);
            }
            QCheckBox::indicator:checked:hover {
                background: rgba(139, 92, 246, 0.7);
            }
        """
        stylesheet = stylesheet.replace("ARROW_UP_PATH", arrow_up)
        stylesheet = stylesheet.replace("ARROW_DOWN_PATH", arrow_down)
        self.setStyleSheet(stylesheet)

        # Settings group box
        group_box = QGroupBox("⚙️ Optimization Settings")
        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(4, 20, 4, 4)

        # Target Size
        self.target_size_spin = QSpinBox()
        self.target_size_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.target_size_spin.setRange(1, 1000)
        self.target_size_spin.setValue(100)
        self.target_size_spin.setSuffix(" KB")
        self.target_size_spin.valueChanged.connect(self._on_settings_changed)
        form_layout.addRow("Target Size:", self.target_size_spin)

        # Output Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WebP", "JPEG", "PNG", "AVIF"])
        self.format_combo.currentTextChanged.connect(self._on_settings_changed)
        form_layout.addRow("Output Format:", self.format_combo)

        # Max Dimension
        self.max_dimension_spin = QSpinBox()
        self.max_dimension_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.max_dimension_spin.setRange(100, 4096)
        self.max_dimension_spin.setValue(1920)
        self.max_dimension_spin.setSuffix(" px")
        self.max_dimension_spin.valueChanged.connect(self._on_settings_changed)
        form_layout.addRow("Max Dimension:", self.max_dimension_spin)

        # Quality Range - Min
        self.min_quality_spin = QSpinBox()
        self.min_quality_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.min_quality_spin.setRange(1, 100)
        self.min_quality_spin.setValue(60)
        self.min_quality_spin.valueChanged.connect(self._on_settings_changed)
        form_layout.addRow("Min Quality:", self.min_quality_spin)

        # Quality Range - Max
        self.max_quality_spin = QSpinBox()
        self.max_quality_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.max_quality_spin.setRange(1, 100)
        self.max_quality_spin.setValue(85)
        self.max_quality_spin.valueChanged.connect(self._on_settings_changed)
        form_layout.addRow("Max Quality:", self.max_quality_spin)

        # Output Directory
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText("optimized")
        self.output_dir_edit.textChanged.connect(self._on_settings_changed)
        output_layout.addWidget(self.output_dir_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.browse_button)

        form_layout.addRow("Output Directory:", output_layout)

        # Watermark
        self.watermark_checkbox = QCheckBox("Add watermark to optimized images")
        self.watermark_checkbox.setChecked(False)
        self.watermark_checkbox.stateChanged.connect(self._on_settings_changed)
        form_layout.addRow("", self.watermark_checkbox)

        # Watermark Text
        self.watermark_text_edit = QLineEdit()
        self.watermark_text_edit.setText("Imagine")
        self.watermark_text_edit.setPlaceholderText("Enter watermark text")
        self.watermark_text_edit.textChanged.connect(self._on_settings_changed)
        form_layout.addRow("Watermark Text:", self.watermark_text_edit)

        # Watermark Position
        self.watermark_position_combo = QComboBox()
        self.watermark_position_combo.addItems([
            "Top Left",
            "Top Right",
            "Bottom Left",
            "Bottom Right",
            "Center"
        ])
        self.watermark_position_combo.setCurrentText("Bottom Right")
        self.watermark_position_combo.currentTextChanged.connect(self._on_settings_changed)
        form_layout.addRow("Watermark Position:", self.watermark_position_combo)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)

        # Info label
        info_label = QLabel(
            "Images will be optimized to the target size while maintaining quality. "
            "The optimizer will automatically adjust dimensions and quality as needed."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

    def _browse_output_dir(self):
        """Show directory picker for output directory."""
        current_dir = self.output_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def _on_settings_changed(self):
        """Handle settings change."""
        self._save_settings()
        self.settings_changed.emit()

    def _save_settings(self):
        """Save settings to QSettings."""
        self.settings.setValue("target_size_kb", self.target_size_spin.value())
        self.settings.setValue("output_format", self.format_combo.currentText())
        self.settings.setValue("max_dimension", self.max_dimension_spin.value())
        self.settings.setValue("min_quality", self.min_quality_spin.value())
        self.settings.setValue("max_quality", self.max_quality_spin.value())
        self.settings.setValue("output_dir", self.output_dir_edit.text())
        self.settings.setValue("watermark", self.watermark_checkbox.isChecked())
        self.settings.setValue("watermark_text", self.watermark_text_edit.text())
        self.settings.setValue("watermark_position", self.watermark_position_combo.currentText())

    def _load_settings(self):
        """Load settings from QSettings."""
        # Block signals during load to avoid triggering changed events
        self.target_size_spin.blockSignals(True)
        self.format_combo.blockSignals(True)
        self.max_dimension_spin.blockSignals(True)
        self.min_quality_spin.blockSignals(True)
        self.max_quality_spin.blockSignals(True)
        self.output_dir_edit.blockSignals(True)
        self.watermark_checkbox.blockSignals(True)
        self.watermark_text_edit.blockSignals(True)
        self.watermark_position_combo.blockSignals(True)

        self.target_size_spin.setValue(
            self.settings.value("target_size_kb", 100, type=int)
        )
        self.format_combo.setCurrentText(
            self.settings.value("output_format", "WebP", type=str)
        )
        self.max_dimension_spin.setValue(
            self.settings.value("max_dimension", 1920, type=int)
        )
        self.min_quality_spin.setValue(
            self.settings.value("min_quality", 60, type=int)
        )
        self.max_quality_spin.setValue(
            self.settings.value("max_quality", 85, type=int)
        )
        self.output_dir_edit.setText(
            self.settings.value("output_dir", "optimized", type=str)
        )
        self.watermark_checkbox.setChecked(
            self.settings.value("watermark", False, type=bool)
        )
        self.watermark_text_edit.setText(
            self.settings.value("watermark_text", "Imagine", type=str)
        )
        self.watermark_position_combo.setCurrentText(
            self.settings.value("watermark_position", "Bottom Right", type=str)
        )

        # Unblock signals
        self.target_size_spin.blockSignals(False)
        self.format_combo.blockSignals(False)
        self.max_dimension_spin.blockSignals(False)
        self.min_quality_spin.blockSignals(False)
        self.max_quality_spin.blockSignals(False)
        self.output_dir_edit.blockSignals(False)
        self.watermark_checkbox.blockSignals(False)
        self.watermark_text_edit.blockSignals(False)
        self.watermark_position_combo.blockSignals(False)

    def get_config(self) -> OptimizationConfig:
        """
        Get OptimizationConfig from current UI state.

        Returns:
            OptimizationConfig object
        """
        # Map UI format name to ImageFormat enum
        format_map = {
            "WebP": ImageFormat.WEBP,
            "JPEG": ImageFormat.JPEG,
            "PNG": ImageFormat.PNG,
            "AVIF": ImageFormat.AVIF,
        }

        # Map UI position name to WatermarkPosition enum
        position_map = {
            "Top Left": WatermarkPosition.TOP_LEFT,
            "Top Right": WatermarkPosition.TOP_RIGHT,
            "Bottom Left": WatermarkPosition.BOTTOM_LEFT,
            "Bottom Right": WatermarkPosition.BOTTOM_RIGHT,
            "Center": WatermarkPosition.CENTER,
        }

        return OptimizationConfig(
            target_size_kb=self.target_size_spin.value(),
            output_format=format_map[self.format_combo.currentText()],
            max_dimension=self.max_dimension_spin.value(),
            min_quality=self.min_quality_spin.value(),
            max_quality=self.max_quality_spin.value(),
            output_dir=self.output_dir_edit.text(),
            watermark=self.watermark_checkbox.isChecked(),
            watermark_text=self.watermark_text_edit.text(),
            watermark_position=position_map[self.watermark_position_combo.currentText()],
        )
