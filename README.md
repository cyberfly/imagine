# Imagine - Image Optimization Tool

A Python-based image optimization tool that intelligently reduces high-resolution images to **<100KB** for web use while maintaining excellent visual quality.

## Features

- **Dual Interface**: Modern PyQt6 GUI (`imagine`) and CLI (`imagine-cli`)
- **Smart Optimization**: Adaptive algorithm that balances quality and file size
- **WebP Support**: Default output in WebP format (25-35% better compression than JPEG)
- **Aspect Ratio Preservation**: Maintains original proportions for all orientations
- **Batch Processing**: Optimize multiple images at once with progress tracking
- **Real-time Feedback**: Visual progress tracking and optimization statistics
- **Drag & Drop**: Easy image loading in GUI mode
- **Safe by Default**: Saves to separate `optimized/` folder, never modifies originals
- **Persistent Settings**: GUI remembers your preferences across sessions

## Installation

### From Source

```bash
# Clone or navigate to the project directory
cd imagine

# Install in development mode
pip install -e .

# Or install with dev dependencies for testing
pip install -e ".[dev]"
```

### Requirements

- Python 3.9 or higher
- Pillow (PIL) for image processing
- PyQt6 for GUI interface
- Click for CLI interface

## Quick Start

### GUI Mode (Recommended)

```bash
# Launch the graphical interface
imagine

# Features:
# - Drag & drop images or use "Add Images" button
# - Configure settings: target size, format, quality
# - Real-time progress tracking
# - View optimization results and statistics
```

### CLI Mode

```bash
# Optimize a single image
imagine-cli optimize photo.jpg

# Optimize multiple images
imagine-cli optimize photos/*.jpg photos/*.png

# Check result
ls -lh optimized/
```

### CLI Options

```bash
# Custom output directory
imagine-cli optimize photo.jpg -d my-optimized/

# Target different file size (in KB)
imagine-cli optimize photo.jpg --target-size 150

# Force JPEG output instead of WebP
imagine-cli optimize photo.jpg --format jpeg

# Show detailed progress
imagine-cli optimize photos/*.jpg --verbose

# Preview without saving
imagine-cli optimize photos/*.jpg --dry-run

# Get image information
imagine-cli info photo.jpg
```

## How It Works

### Optimization Algorithm

Imagine uses an **adaptive multi-pass strategy**:

1. **Analysis Phase**
   - Reads image dimensions, format, and EXIF data
   - Auto-rotates based on EXIF orientation
   - Determines orientation (landscape/portrait/square)

2. **Dimension Optimization**
   - **Landscape**: Max width 1920px (maintains aspect ratio)
   - **Portrait**: Max height 1920px (maintains aspect ratio)
   - **Square**: Max 1920x1920px
   - Rationale: 1920px matches modern displays; larger wastes bandwidth

3. **Compression Strategy**
   ```
   Start with quality=85
   While file size > target AND quality > 60:
       Reduce quality by 5
       Re-encode to WebP
       Check file size

   If still > target:
       Reduce dimensions by 10%
       Retry compression loop

   Stop when: target reached OR quality < 60 OR dimensions < 50% original
   ```

4. **Format Selection**
   - **Primary**: WebP (superior compression)
   - **Fallback**: JPEG (if specified)
   - **Transparency**: Preserves alpha channel in WebP/PNG

### Why These Defaults?

- **<100KB target**: Fast loading on all connections, including mobile
- **WebP format**: 25-35% smaller than JPEG at equivalent quality
- **1920px max**: Matches 1080p displays; larger is excessive for web
- **Quality ≥60**: Below this, compression artifacts become visible
- **Separate folder**: Protects originals, easy before/after comparison

## CLI Reference

### Main Command: `optimize`

```
imagine-cli optimize [OPTIONS] IMAGES...

Options:
  -d, --output-dir PATH           Output directory [default: optimized]
  --target-size INTEGER           Target file size in KB [default: 100]
  --format [webp|jpeg|png]        Output format [default: webp]
  --max-dimension INTEGER         Max width/height in pixels [default: 1920]
  --min-quality INTEGER           Minimum quality (1-100) [default: 60]
  --max-quality INTEGER           Starting quality (1-100) [default: 85]
  -v, --verbose                   Show detailed information
  --dry-run                       Preview without saving
  --help                          Show help message
```

### Info Command: `info`

```
imagine-cli info IMAGE

Display information about an image:
- Dimensions
- Format
- File size
- Orientation
- Transparency
- EXIF data
```

## Examples

### Optimize for Different Use Cases

```bash
# Standard web optimization
imagine-cli optimize hero-image.jpg
# Result: optimized/hero-image.webp (<100KB)

# Smaller target for thumbnails
imagine-cli optimize thumbnail.jpg --target-size 50

# Preserve maximum quality
imagine-cli optimize product.png --min-quality 80 --max-quality 95

# Smaller max dimension for mobile
imagine-cli optimize mobile-banner.jpg --max-dimension 1280

# JPEG output for compatibility
imagine-cli optimize photo.jpg --format jpeg
```

### Batch Processing

```bash
# Optimize all images in a directory
imagine-cli optimize photos/*

# Specific formats only
imagine-cli optimize *.jpg *.png

# With progress and summary
imagine-cli optimize gallery/*.jpg --verbose

# Custom output location
imagine-cli optimize products/* -d ../website/images/optimized/
```

### Check Before Processing

```bash
# Preview what would be processed
imagine-cli optimize photos/* --dry-run

# Get info about an image
imagine-cli info large-photo.jpg
```

## Architecture

### Clean Separation of Concerns

The project is designed with a clean separation between core logic and UI:

```
imagine/
├── core/              # UI-agnostic image processing
│   ├── optimizer.py   # Main ImageOptimizer class
│   ├── strategy.py    # AdaptiveStrategy algorithm
│   ├── processor.py   # Low-level Pillow operations
│   ├── analyzer.py    # Image analysis
│   └── config.py      # Dataclasses for config and results
├── gui/               # PyQt6 GUI interface
│   ├── app.py         # Application entry point
│   ├── main_window.py # Main window layout
│   ├── widgets/       # Custom widgets (settings, progress, image list)
│   ├── workers/       # Background optimization workers
│   ├── models/        # Data models
│   └── utils/         # GUI utilities and theming
├── cli/               # CLI interface (Click)
│   └── main.py
└── utils/             # Shared utilities
```

### Using the Core in Your Application

The core can be easily integrated into any Python application:

```python
from imagine.core.optimizer import ImageOptimizer
from imagine.core.config import OptimizationConfig

# In your application
config = OptimizationConfig(target_size_kb=100)
optimizer = ImageOptimizer(config)

# With progress callback
def update_progress(current, total):
    progress_bar.setValue(current / total * 100)

result = optimizer.optimize(
    input_path,
    output_path,
    callback=update_progress
)

# Display result
print(f"Size reduced by {result.size_reduction_percent:.1f}%")
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=imagine --cov-report=html
```

### Project Structure

- `imagine/core/` - Core optimization logic (UI-agnostic)
- `imagine/gui/` - PyQt6 graphical interface
- `imagine/cli/` - Command-line interface
- `tests/` - Test suite
- `pyproject.toml` - Project configuration and dependencies

## Troubleshooting

### "Command not found: imagine" or "Command not found: imagine-cli"

Make sure you installed the package:
```bash
pip install -e .
```

Or run directly:
```bash
# GUI mode
python -m imagine.gui.app

# CLI mode
python -m imagine.cli.main optimize photo.jpg
```

### Images still over 100KB

Some images may be difficult to compress below 100KB while maintaining quality ≥60. Try:
- Reducing `--target-size`
- Lowering `--min-quality` (may reduce visual quality)
- Using `--format jpeg` (WebP is usually better though)
- Reducing `--max-dimension`

### WebP not supported

WebP is supported by all modern browsers (Chrome, Firefox, Safari, Edge). For legacy support, use `--format jpeg`.

## License

MIT License - feel free to use in personal and commercial projects.

## Contributing

Contributions welcome! Areas for improvement:
- Additional output formats (AVIF, HEIC)
- More optimization strategies
- GUI enhancements (before/after preview, batch comparison)
- Performance optimizations
- Additional test coverage
- macOS native app packaging

## Future Roadmap

- [x] GUI with drag-and-drop interface
- [x] Real-time progress tracking
- [x] Persistent settings
- [ ] Before/after image comparison in GUI
- [ ] Custom optimization profiles
- [ ] AVIF format support
- [ ] Advanced EXIF preservation options
- [ ] Native Mac app bundle
- [ ] Integration with popular frameworks (Next.js, etc.)
