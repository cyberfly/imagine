"""Background worker for image optimization."""

from pathlib import Path
from typing import List

from PyQt6.QtCore import QThread, pyqtSignal

from imagine.core.config import OptimizationConfig, OptimizationResult
from imagine.core.optimizer import ImageOptimizer
from imagine.gui.models.image_item import ImageItem


class OptimizerWorker(QThread):
    """
    QThread worker for background image optimization.

    Signals:
        progress_updated: Emitted with (current, total) when progress changes
        image_started: Emitted with filename when starting to process an image
        image_completed: Emitted with OptimizationResult when image is done
        batch_completed: Emitted with list of results when batch is done
        error_occurred: Emitted with (filename, error_message) on error
    """

    # Signals
    progress_updated = pyqtSignal(int, int)  # current, total
    image_started = pyqtSignal(str)  # filename
    image_completed = pyqtSignal(OptimizationResult)  # result
    batch_completed = pyqtSignal(list)  # list of results
    error_occurred = pyqtSignal(str, str)  # filename, error_message

    def __init__(self, items: List[ImageItem], config: OptimizationConfig):
        """
        Initialize worker.

        Args:
            items: List of ImageItem objects to process
            config: Optimization configuration
        """
        super().__init__()
        self.items = items
        self.config = config
        self.optimizer = ImageOptimizer(config)
        self._cancel_requested = False

    def run(self):
        """Run the optimization batch in the background."""
        results = []
        total = len(self.items)

        # Ensure output directory exists
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for idx, item in enumerate(self.items, 1):
            # Check for cancellation
            if self._cancel_requested:
                break

            # Emit start signal
            self.image_started.emit(item.filename)

            try:
                # Generate output path
                output_path = output_dir / self._generate_output_filename(item.path)

                # Optimize image
                result = self.optimizer.optimize(item.path, output_path)
                results.append(result)

                # Emit completion signal
                self.image_completed.emit(result)

                # Emit progress
                self.progress_updated.emit(idx, total)

            except Exception as e:
                # Emit error signal
                self.error_occurred.emit(item.filename, str(e))

                # Create failure result
                failure_result = OptimizationResult(
                    input_path=item.path,
                    output_path=Path("unknown"),
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
                results.append(failure_result)
                self.image_completed.emit(failure_result)

                # Still update progress
                self.progress_updated.emit(idx, total)

        # Emit batch completion
        self.batch_completed.emit(results)

    def cancel(self):
        """Request cancellation of the optimization process."""
        self._cancel_requested = True

    def _generate_output_filename(self, input_path: Path) -> str:
        """
        Generate output filename with correct extension.

        Args:
            input_path: Input image path

        Returns:
            Output filename string
        """
        stem = input_path.stem
        ext = self.config.output_format.value
        return f"{stem}.{ext}"
