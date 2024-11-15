import os

import cairosvg
from PIL import Image


def convert_svg(input_path, output_format='png', width=None, height=None):
    """
    Convert SVG to PNG or JPEG with specified dimensions
    
    Parameters:
    input_path (str): Path to input SVG file
    output_format (str): 'png' or 'jpeg'
    width (int): Desired width in pixels
    height (int): Desired height in pixels
    """
    
    # Generate output filename
    filename = os.path.splitext(input_path)[0]
    temp_output = f"{filename}_temp.png"
    final_output = f"{filename}.{output_format.lower()}"
    
    # Convert SVG to PNG first (CairoSVG doesn't support direct JPEG conversion)
    cairosvg.svg2png(
        url=input_path, 
        write_to=temp_output,
        output_width=width if width else None,
        output_height=height if height else None
    )
    
    # Open with PIL for resizing and possible JPEG conversion
    with Image.open(temp_output) as img:
        # Calculate height if only width is specified (only needed if no dimensions were provided)
        if not width and not height:
            width = img.width
            height = img.height
        # Calculate width if only height is specified
        elif height and not width:
            ratio = height / img.height
            width = int(img.width * ratio)
            
        # Resize if dimensions are specified
        if width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
        # Convert to RGB if saving as JPEG
        if output_format.lower() == 'jpeg':
            img = img.convert('RGB')
            
        # Save final image
        img.save(final_output, format=output_format.upper())
    
    # Remove temporary PNG if converting to JPEG
    if output_format.lower() == 'jpeg':
        os.remove(temp_output)

# Example usage
if __name__ == "__main__":
    convert_svg('./examples/logout.svg', output_format='png', width=1024, height=1024)