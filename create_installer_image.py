from PIL import Image, ImageDraw, ImageFont
import os

def create_installer_image():
    """Create a welcome image for the Windows installer."""
    
    # Create a new image with the required dimensions (164x314 pixels for NSIS)
    width, height = 164, 314
    image = Image.new('RGB', (width, height), color=(33, 39, 55))  # Dark blue background
    
    # Create a drawing object
    draw = ImageDraw.Draw(image)
    
    # Add a gradient effect
    for y in range(height):
        # Create a subtle gradient
        color = (33, 39, 55 + int(y * 20 / height))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Try to load a font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        text_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Add title text
    title = "Secure Submission System"
    title_width = title_font.getbbox(title)[2]
    draw.text(((width - title_width) // 2, 40), title, font=title_font, fill=(255, 255, 255))
    
    # Add version text
    version = "Version 1.0.0"
    version_width = text_font.getbbox(version)[2]
    draw.text(((width - version_width) // 2, 70), version, font=text_font, fill=(200, 200, 200))
    
    # Add a simple logo/icon (a rectangle with rounded corners)
    draw.rounded_rectangle([(width//2 - 40, 130), (width//2 + 40, 210)], radius=10, 
                          fill=(74, 123, 247))  # Blue color
    
    # Add a smaller rectangle inside (representing a document)
    draw.rounded_rectangle([(width//2 - 25, 150), (width//2 + 25, 190)], radius=5, 
                          fill=(255, 255, 255))  # White color
    
    # Add some lines representing text in the document
    draw.line([(width//2 - 15, 160), (width//2 + 15, 160)], fill=(74, 123, 247), width=2)
    draw.line([(width//2 - 15, 170), (width//2 + 15, 170)], fill=(74, 123, 247), width=2)
    draw.line([(width//2 - 15, 180), (width//2 + 5, 180)], fill=(74, 123, 247), width=2)
    
    # Add bottom text
    bottom_text = "Installation Wizard"
    bottom_width = text_font.getbbox(bottom_text)[2]
    draw.text(((width - bottom_width) // 2, height - 50), bottom_text, 
             font=text_font, fill=(200, 200, 200))
    
    # Ensure the static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Save the image
    image_path = 'static/installer-welcome.bmp'
    image.save(image_path)
    print(f"Installer welcome image created at: {image_path}")
    
    return image_path

if __name__ == "__main__":
    create_installer_image()