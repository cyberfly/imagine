"""Image item data model for GUI."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from imagine.core.config import OptimizationResult


class ProcessingStatus(Enum):
    """Processing status for image items."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class ImageItem:
    """
    Data model for an image in the processing list.

    Attributes:
        path: Path to the image file
        status: Current processing status
        result: Optimization result (if processed)
    """
    path: Path
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[OptimizationResult] = None

    @property
    def filename(self) -> str:
        """Display name for the image."""
        return self.path.name

    @property
    def original_size_kb(self) -> Optional[float]:
        """Original file size in KB."""
        if self.result:
            return self.result.original_size_kb
        try:
            return self.path.stat().st_size / 1024
        except:
            return None

    @property
    def optimized_size_kb(self) -> Optional[float]:
        """Optimized file size in KB (if available)."""
        if self.result and self.result.success:
            return self.result.optimized_size_kb
        return None

    @property
    def status_icon(self) -> str:
        """Unicode icon for current status."""
        icons = {
            ProcessingStatus.PENDING: "○",
            ProcessingStatus.PROCESSING: "⟳",
            ProcessingStatus.SUCCESS: "✓",
            ProcessingStatus.ERROR: "✗",
        }
        return icons.get(self.status, "○")

    @property
    def size_display(self) -> str:
        """Display string for file sizes."""
        orig = self.original_size_kb
        opt = self.optimized_size_kb

        if orig is None:
            return "?"

        if opt is None:
            return f"{orig:.1f} KB"

        return f"{orig:.1f} KB → {opt:.1f} KB"

    @property
    def error_message(self) -> Optional[str]:
        """Error message if processing failed."""
        if self.result and not self.result.success:
            return self.result.error_message
        return None
