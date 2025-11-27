import os

import numpy as np
from PIL import Image
from skimage import measure
from skimage.measure import approximate_polygon


def straighten_lines(contour, distance_threshold=2.0):
    """
    Straighten nearly-straight line segments in a contour.
    
    Parameters:
    contour: Array of (y, x) points
    distance_threshold: Maximum distance from line to consider points collinear
    
    Returns:
    Simplified contour with straightened lines
    """
    if len(contour) < 3:
        return contour
    
    result = [contour[0]]
    i = 0
    
    while i < len(contour) - 1:
        # Start a new line segment
        start = contour[i]
        
        # Find the furthest point that's still roughly collinear
        best_end = i + 1
        
        for j in range(i + 2, len(contour)):  # Look ahead to all remaining points
            end = contour[j]
            
            # Check if all intermediate points are close to the line start->end
            all_collinear = True
            for k in range(i + 1, j):
                point = contour[k]
                # Calculate distance from point to line
                line_vec = end - start
                line_len = np.linalg.norm(line_vec)
                if line_len < 1e-6:
                    continue
                line_unit = line_vec / line_len
                point_vec = point - start
                proj_len = np.dot(point_vec, line_unit)
                proj = start + proj_len * line_unit
                dist = np.linalg.norm(point - proj)
                
                if dist > distance_threshold:
                    all_collinear = False
                    break
            
            if all_collinear:
                best_end = j
            else:
                break
        
        # Add the end point of this line segment
        result.append(contour[best_end])
        i = best_end
    
    return np.array(result)


def snap_to_angles(contour, snap_angles=[0, 30, 60, 90, 120, 150, 180], tolerance=5):
    """
    Snap line segments to common angles (useful for geometric logos).
    
    Parameters:
    contour: Array of (y, x) points
    snap_angles: List of angles to snap to (in degrees)
    tolerance: Maximum angle deviation to snap (in degrees)
    
    Returns:
    Contour with angles snapped to nearest common angle
    """
    if len(contour) < 2:
        return contour
    
    result = [contour[0]]
    
    for i in range(1, len(contour)):
        prev = result[-1]
        curr = contour[i]
        
        # Calculate current angle
        dy = curr[0] - prev[0]
        dx = curr[1] - prev[1]
        length = np.sqrt(dx*dx + dy*dy)
        
        if length < 1e-6:
            continue
            
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Find nearest snap angle
        best_snap = angle
        min_diff = float('inf')
        for snap in snap_angles:
            for offset in [0, 180, -180]:
                diff = abs(angle - (snap + offset))
                if diff < min_diff:
                    min_diff = diff
                    best_snap = snap + offset
        
        # Snap if within tolerance
        if min_diff <= tolerance:
            new_angle = np.radians(best_snap)
            new_point = np.array([
                prev[0] + length * np.sin(new_angle),
                prev[1] + length * np.cos(new_angle)
            ])
            result.append(new_point)
        else:
            result.append(curr)
    
    return np.array(result)


def extract_gradient_colors(img, mask):
    """
    Extract gradient colors from the image based on the mask.
    Returns top and bottom colors for a vertical gradient.
    """
    rgb = np.array(img.convert("RGB"))
    
    # Find rows that have masked pixels
    rows_with_content = np.any(mask, axis=1)
    row_indices = np.where(rows_with_content)[0]
    
    if len(row_indices) < 2:
        return None, None
    
    top_row = row_indices[0]
    bottom_row = row_indices[-1]
    
    # Sample colors from top and bottom regions
    top_region = mask[top_row:top_row + 20, :]
    bottom_region = mask[bottom_row - 20:bottom_row, :]
    
    # Get average color from top
    top_pixels = rgb[top_row:top_row + 20, :][top_region]
    if len(top_pixels) > 0:
        top_color = np.mean(top_pixels, axis=0).astype(int)
    else:
        top_color = np.array([76, 175, 80])  # Default green
    
    # Get average color from bottom
    bottom_pixels = rgb[bottom_row - 20:bottom_row, :][bottom_region]
    if len(bottom_pixels) > 0:
        bottom_color = np.mean(bottom_pixels, axis=0).astype(int)
    else:
        bottom_color = np.array([56, 142, 60])  # Default darker green
    
    return top_color, bottom_color


def convert_png_to_svg(png_path, svg_path=None, threshold=200, fill_color="black", mode="auto", simplify=1.0, straighten=False, gradient=False):
    """
    Convert PNG to SVG using contour detection
    
    Parameters:
    png_path (str): Path to input PNG file
    svg_path (str): Path to output SVG file (optional, defaults to same name with .svg extension)
    threshold (int): Threshold for detecting shapes (0-255, default 200)
    fill_color (str): Fill color for the SVG paths (default "black", ignored if gradient=True)
    mode (str): Detection mode - "auto", "dark", "light", or "alpha"
    simplify (float): Path simplification tolerance (default 1.0, higher = simpler paths)
    straighten (bool): Apply line straightening algorithm (default False)
    gradient (bool): Extract and apply gradient from original image (default False)
    
    Returns:
    str: Path to the output SVG file
    """
    # Generate output filename if not provided
    if svg_path is None:
        svg_path = os.path.splitext(png_path)[0] + ".svg"
    
    # Open image
    img = Image.open(png_path)
    width, height = img.size
    
    # Determine the best detection mode
    if mode == "auto":
        if img.mode == "RGBA":
            # Check if image has meaningful alpha channel
            alpha = np.array(img.split()[-1])
            if np.any((alpha > 10) & (alpha < 245)):
                mode = "alpha"
            else:
                mode = "color"
        else:
            mode = "color"
    
    # Create mask based on mode
    if mode == "alpha" and img.mode == "RGBA":
        # Use alpha channel - detect non-transparent pixels
        alpha = np.array(img.split()[-1])
        mask = alpha > threshold
    elif mode == "dark":
        # Detect dark pixels (original behavior)
        gray = np.array(img.convert("L"))
        mask = gray < threshold
    elif mode == "light":
        # Detect light pixels
        gray = np.array(img.convert("L"))
        mask = gray > threshold
    else:
        # Color mode: detect non-white/non-background pixels
        if img.mode == "RGBA":
            # For RGBA, use alpha channel primarily
            alpha = np.array(img.split()[-1])
            mask = alpha > 128
        else:
            # For RGB, detect non-white pixels
            rgb = np.array(img.convert("RGB"))
            # Calculate distance from white (255, 255, 255)
            white_dist = np.sqrt(np.sum((rgb.astype(float) - 255) ** 2, axis=2))
            mask = white_dist > (255 - threshold)
    
    # Find contours at 0.5 level
    contours = measure.find_contours(mask.astype(float), 0.5)
    
    if not contours:
        print(f"Warning: No contours found in {png_path}")
        # Create empty SVG
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"></svg>'
    else:
        # Sort contours by area (largest first) to handle holes properly
        contour_areas = []
        for contour in contours:
            # Calculate approximate area using shoelace formula
            x = contour[:, 1]
            y = contour[:, 0]
            area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
            contour_areas.append((area, contour))
        
        contour_areas.sort(key=lambda x: x[0], reverse=True)
        
        # Build SVG with fill-rule evenodd to handle holes
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">\n'
        
        # Add gradient definition if enabled
        if gradient:
            top_color, bottom_color = extract_gradient_colors(img, mask)
            if top_color is not None:
                top_hex = f"#{top_color[0]:02x}{top_color[1]:02x}{top_color[2]:02x}"
                bottom_hex = f"#{bottom_color[0]:02x}{bottom_color[1]:02x}{bottom_color[2]:02x}"
                svg += '  <defs>\n'
                svg += '    <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">\n'
                svg += f'      <stop offset="0%" style="stop-color:{top_hex};stop-opacity:1" />\n'
                svg += f'      <stop offset="100%" style="stop-color:{bottom_hex};stop-opacity:1" />\n'
                svg += '    </linearGradient>\n'
                svg += '  </defs>\n'
                fill_attr = 'url(#grad)'
            else:
                fill_attr = fill_color
        else:
            fill_attr = fill_color
        
        # Combine all contours into a single path with evenodd fill rule
        all_paths = []
        for _, contour in contour_areas:
            # Simplify the contour to reduce points
            if simplify > 0:
                contour = approximate_polygon(contour, tolerance=simplify)
            
            # Apply line straightening if enabled
            if straighten:
                contour = straighten_lines(contour)
                contour = snap_to_angles(contour)
            
            # Skip very small contours (noise)
            if len(contour) < 3:
                continue
                
            # Build path data (note: skimage returns y,x coordinates)
            path_data = "M " + " L ".join(f"{x:.2f},{y:.2f}" for y, x in contour) + " Z"
            all_paths.append(path_data)
        
        combined_path = " ".join(all_paths)
        svg += f'  <path d="{combined_path}" fill="{fill_attr}" fill-rule="evenodd"/>\n'
        svg += "</svg>"
    
    # Write SVG file
    with open(svg_path, "w") as f:
        f.write(svg)
    
    print(f"Converted {png_path} to {svg_path}")
    return svg_path


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert PNG to SVG using contour detection")
    parser.add_argument("input", help="Path to input PNG file")
    parser.add_argument("-o", "--output", help="Path to output SVG file (default: same name with .svg extension)")
    parser.add_argument("-t", "--threshold", type=int, default=200, help="Threshold (0-255, default: 200)")
    parser.add_argument("-c", "--color", default="black", help="Fill color for SVG paths (default: black)")
    parser.add_argument("-m", "--mode", choices=["auto", "dark", "light", "alpha", "color"], 
                        default="auto", help="Detection mode (default: auto)")
    parser.add_argument("-s", "--simplify", type=float, default=1.0,
                        help="Path simplification tolerance (default: 1.0, higher = simpler)")
    parser.add_argument("--straighten", action="store_true",
                        help="Apply line straightening algorithm for geometric shapes")
    parser.add_argument("--gradient", action="store_true",
                        help="Extract and apply gradient from original image")
    
    args = parser.parse_args()
    
    convert_png_to_svg(args.input, args.output, args.threshold, args.color, args.mode, args.simplify, args.straighten, args.gradient)
