# Imagine - Image Optimization Tool

A Python-based image optimization tool that intelligently reduces high-resolution images to **<100KB** for web use while maintaining excellent visual quality.

![Imagine GUI](screenshot.png)

## Features

- **Dual Interface**: Modern PyQt6 GUI (`imagine`) and CLI (`imagine-cli`)
- **Smart Optimization**: Adaptive algorithm that balances quality and file size
- **Multiple Formats**: WebP, AVIF, JPEG, and PNG output support
- **WebP & AVIF Support**: Modern formats with superior compression (25-35% better than JPEG)
- **Watermark Support**: Add customizable text watermarks with flexible positioning
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

# Add watermark
imagine-cli optimize photo.jpg --watermark --watermark-text "© 2026"

# Watermark with custom position
imagine-cli optimize photo.jpg --watermark --watermark-position center

# Show detailed progress
imagine-cli optimize photos/*.jpg --verbose

# Preview without saving
imagine-cli optimize photos/*.jpg --dry-run

# Get image information
imagine-cli info photo.jpg
```

## CLI Reference

### Main Command: `optimize`

```
imagine-cli optimize [OPTIONS] IMAGES...

Options:
  -d, --output-dir PATH           Output directory [default: optimized]
  --target-size INTEGER           Target file size in KB [default: 100]
  --format [webp|jpeg|png|avif]   Output format [default: webp]
  --max-dimension INTEGER         Max width/height in pixels [default: 1920]
  --min-quality INTEGER           Minimum quality (1-100) [default: 60]
  --max-quality INTEGER           Starting quality (1-100) [default: 85]
  --watermark                     Add watermark to images
  --watermark-text TEXT           Watermark text [default: Imagine]
  --watermark-position            Position: top-left, top-right, bottom-left,
                                  bottom-right, center [default: bottom-right]
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

# Add copyright watermark
imagine-cli optimize photo.jpg --watermark --watermark-text "© 2026 MyCompany"

# Center watermark for portfolio images
imagine-cli optimize portfolio.jpg --watermark --watermark-text "John Doe Photography" --watermark-position center

# Top-right watermark
imagine-cli optimize screenshot.png --watermark --watermark-position top-right

# Smaller target for thumbnails
imagine-cli optimize thumbnail.jpg --target-size 50

# Preserve maximum quality
imagine-cli optimize product.png --min-quality 80 --max-quality 95

# Smaller max dimension for mobile
imagine-cli optimize mobile-banner.jpg --max-dimension 1280

# JPEG output for compatibility
imagine-cli optimize photo.jpg --format jpeg

# AVIF output for maximum compression (newer browsers)
imagine-cli optimize photo.jpg --format avif
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

### WebP/AVIF not supported

WebP and AVIF are supported by all modern browsers (Chrome, Firefox, Safari, Edge). AVIF offers even better compression than WebP but has slightly less browser support. For legacy support, use `--format jpeg`.

## License

MIT License - feel free to use in personal and commercial projects.

## Contributing

Contributions welcome! Areas for improvement:
- Additional output formats (HEIC)
- More optimization strategies
- GUI enhancements (before/after preview, batch comparison)
- Performance optimizations
- Additional test coverage
- macOS native app packaging

## Future Roadmap

- [x] GUI with drag-and-drop interface
- [x] Real-time progress tracking
- [x] Persistent settings
- [x] AVIF format support
- [ ] Before/after image comparison in GUI
- [ ] Custom optimization profiles
- [ ] Advanced EXIF preservation options
- [ ] Native Mac app bundle
- [ ] Integration with popular frameworks (Next.js, etc.)
