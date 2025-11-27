# SVG Converter

A simple Python tool to convert between SVG and raster image formats.

## Features

- Convert SVG to PNG or JPEG
- Convert PNG to SVG (using contour detection)
- Customize output dimensions
- Maintain aspect ratio
- Adjustable threshold for PNG to SVG conversion

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/svg-converter.git
cd svg-converter
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### SVG to PNG/JPEG

```python
from src.converter import convert_svg

# Convert to PNG (1024x1024)
convert_svg('input.svg', output_format='png', width=1024, height=1024)

# Convert to JPEG (maintain aspect ratio)
convert_svg('input.svg', output_format='jpeg', width=800)
```

### PNG to SVG

**CLI usage:**

```bash
# Basic usage (output will be same name with .svg extension)
python src/png_to_svg.py logo.png

# With custom output path
python src/png_to_svg.py logo.png -o output/logo.svg

# Capture more detail and keep straight edges
python src/png_to_svg.py logo.png -s 0.1 --straighten

# Match original gradient and color
python src/png_to_svg.py logo.png --gradient --straighten

# Tune threshold and color manually
python src/png_to_svg.py logo.png -t 180 -c "#333333"

# Show help
python src/png_to_svg.py --help
```

**Python usage:**

```python
from src.png_to_svg import convert_png_to_svg

# Basic usage (output will be same name with .svg extension)
convert_png_to_svg('logo.png')

# With custom output path
convert_png_to_svg('logo.png', 'output/logo.svg')

# With custom threshold and fill color
convert_png_to_svg('logo.png', threshold=180, fill_color="#333333")

# With gradient extraction and line straightening
convert_png_to_svg('logo.png', simplify=0.1, straighten=True, gradient=True)
```

**CLI Options:**

- `-o, --output`: Output SVG path (default: same name with .svg extension)
- `-t, --threshold`: Grayscale threshold 0-255 (default: 200)
- `-c, --color`: Fill color for SVG paths (default: black)
- `-s, --simplify`: Path simplification tolerance (lower = more detail)
- `--straighten`: Attempts to keep lines straight and snap to common angles
- `--gradient`: Extracts a vertical gradient from the source PNG and applies it to the SVG fill

## Requirements

- Python 3.7+
- cairo library (system dependency)
- Python packages (see requirements.txt)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request
