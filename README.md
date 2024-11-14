# SVG Converter

A simple Python tool to convert SVG files to PNG or JPEG with customizable dimensions.

## Features

- Convert SVG to PNG or JPEG
- Customize output dimensions
- Maintain aspect ratio
- Batch conversion support

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

Basic usage:

```python
from src.converter import convert_svg

# Convert to PNG (1024x1024)
convert_svg('input.svg', output_format='png', width=1024, height=1024)

# Convert to JPEG (maintain aspect ratio)
convert_svg('input.svg', output_format='jpeg', width=800)
```

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
