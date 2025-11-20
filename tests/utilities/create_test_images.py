import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Create test images directory
TEST_ASSETS_DIR = Path(__file__).resolve().parent / "test_assets"
TEST_ASSETS_DIR.mkdir(exist_ok=True)

def create_text_image(text, filename):
    """Create a test image with the given text."""
    # Create a white image with black text
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to default if unavailable
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((10, 35), text, fill='black', font=font)
    
    # Save as PNG
    img.save(filename)
    print(f"Created: {filename}")

# Create test images
create_text_image("Allow", TEST_ASSETS_DIR / "allow_text.png")
create_text_image("Click Here", TEST_ASSETS_DIR / "no_allow_text.png")
create_text_image("Allow Button", TEST_ASSETS_DIR / "allow_with_button.png")
create_text_image("Disallow", TEST_ASSETS_DIR / "disallow_text.png")

# Create a blank image (no text)
blank_img = Image.new('RGB', (200, 100), color='white')
blank_img.save(TEST_ASSETS_DIR / "blank.png")
print(f"Created: {TEST_ASSETS_DIR / 'blank.png'}")

print(f"\nTest images created in: {TEST_ASSETS_DIR}")
