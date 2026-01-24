# Imagine - Image Optimization Tool

A Python-based image optimization tool that intelligently reduces high-resolution images to **<100KB** for web use while maintaining excellent visual quality.

## Features

- **Smart Optimization**: Adaptive algorithm that balances quality and file size
- **WebP Support**: Default output in WebP format (25-35% better compression than JPEG)
- **Aspect Ratio Preservation**: Maintains original proportions for all orientations
- **Batch Processing**: Optimize multiple images at once with progress tracking
- **Safe by Default**: Saves to separate `optimized/` folder, never modifies originals
- **CLI Interface**: Simple command-line interface with extensive options
- **Future-Ready**: Core architecture designed for easy GUI integration

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
- Click for CLI interface

## Quick Start

### Basic Usage

```bash
# Optimize a single image
imagine optimize photo.jpg

# Optimize multiple images
imagine optimize photos/*.jpg photos/*.png

# Check result
ls -lh optimized/
```

### Common Options

```bash
# Custom output directory
imagine optimize photo.jpg -d my-optimized/

# Target different file size (in KB)
imagine optimize photo.jpg --target-size 150

# Force JPEG output instead of WebP
imagine optimize photo.jpg --format jpeg

# Show detailed progress
imagine optimize photos/*.jpg --verbose

# Preview without saving
imagine optimize photos/*.jpg --dry-run

# Get image information
imagine info photo.jpg
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
imagine optimize [OPTIONS] IMAGES...

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
imagine info IMAGE

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
imagine optimize hero-image.jpg
# Result: optimized/hero-image.webp (<100KB)

# Smaller target for thumbnails
imagine optimize thumbnail.jpg --target-size 50

# Preserve maximum quality
imagine optimize product.png --min-quality 80 --max-quality 95

# Smaller max dimension for mobile
imagine optimize mobile-banner.jpg --max-dimension 1280

# JPEG output for compatibility
imagine optimize photo.jpg --format jpeg
```

### Batch Processing

```bash
# Optimize all images in a directory
imagine optimize photos/*

# Specific formats only
imagine optimize *.jpg *.png

# With progress and summary
imagine optimize gallery/*.jpg --verbose

# Custom output location
imagine optimize products/* -d ../website/images/optimized/
```

### Check Before Processing

```bash
# Preview what would be processed
imagine optimize photos/* --dry-run

# Get info about an image
imagine info large-photo.jpg
```

## Architecture

### UI-Agnostic Core

The project is designed with a clean separation between core logic and UI:

```
imagine/
├── core/              # UI-agnostic image processing
│   ├── optimizer.py   # Main ImageOptimizer class
│   ├── strategy.py    # AdaptiveStrategy algorithm
│   ├── processor.py   # Low-level Pillow operations
│   ├── analyzer.py    # Image analysis
│   └── config.py      # Dataclasses for config and results
├── cli/               # CLI interface (Click)
│   └── main.py
└── utils/             # Shared utilities
```

### Future GUI Integration

The core can be easily integrated into a native Mac app:

```python
from imagine.core.optimizer import ImageOptimizer
from imagine.core.config import OptimizationConfig

# In your GUI application
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
- `imagine/cli/` - Command-line interface
- `tests/` - Test suite
- `pyproject.toml` - Project configuration and dependencies

## Troubleshooting

### "Command not found: imagine"

Make sure you installed the package:
```bash
pip install -e .
```

Or run directly:
```bash
python -m imagine optimize photo.jpg
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
- Additional output formats
- More optimization strategies
- GUI implementation
- Performance optimizations
- Additional test coverage

## Future Roadmap

- [ ] Native Mac app with drag-and-drop interface
- [ ] Batch preview with before/after comparison
- [ ] Custom optimization profiles
- [ ] AVIF format support
- [ ] Advanced EXIF preservation options
- [ ] Integration with popular frameworks (Next.js, etc.)
