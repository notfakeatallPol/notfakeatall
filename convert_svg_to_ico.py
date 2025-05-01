import os
import cairosvg
from PIL import Image

def convert_svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert SVG to ICO with multiple sizes."""
    # Create a temporary directory for PNG files
    temp_dir = 'temp_icons'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Generate PNGs of different sizes
    png_files = []
    for size in sizes:
        png_path = os.path.join(temp_dir, f'icon_{size}.png')
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
        png_files.append(png_path)
    
    # Open all PNG images
    images = [Image.open(png) for png in png_files]
    
    # Save as ICO
    images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images], append_images=images[1:])
    
    # Clean up temporary files
    for png in png_files:
        os.remove(png)
    os.rmdir(temp_dir)
    
    print(f"Converted {svg_path} to {ico_path}")

if __name__ == "__main__":
    convert_svg_to_ico('static/favicon.svg', 'static/favicon.ico')