from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create base image with transparency
    size = 1024  # Standard size for macOS icons
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Define colors
    primary_color = (58, 125, 68)  # Green to match app theme (#3a7d44)
    secondary_color = (224, 224, 224)  # Light gray (#e0e0e0)
    
    # Draw a rounded rectangle (document shape)
    padding = size // 8
    rect_coords = [padding, padding, size - padding, size - padding]
    draw.rounded_rectangle(rect_coords, radius=size//16, fill=secondary_color)
    
    # Draw scan line
    scan_height = size // 8
    scan_y = size // 2 - scan_height // 2
    draw.rectangle([padding, scan_y, size - padding, scan_y + scan_height], 
                  fill=primary_color)
    
    # Draw text lines
    line_height = size // 16
    line_padding = size // 32
    line_width = size - (padding * 3)
    
    # Draw text lines above scan line
    for i in range(3):
        y = scan_y - (line_height + line_padding) * (i + 1)
        draw.rectangle([padding * 1.5, y, padding * 1.5 + line_width * 0.8, y + line_height], 
                      fill=primary_color)
    
    # Draw text lines below scan line
    for i in range(3):
        y = scan_y + scan_height + (line_height + line_padding) * i
        draw.rectangle([padding * 1.5, y, padding * 1.5 + line_width * 0.7, y + line_height], 
                      fill=primary_color)
    
    # Save as PNG for menu bar (larger size for better visibility)
    menu_bar_size = (32, 32)  # Increased from 22x22 to 32x32
    menu_bar_image = image.resize(menu_bar_size, Image.Resampling.LANCZOS)
    menu_bar_image.save('menu_bar_icon.png')
    
    # Save as PNG in various sizes for ICNS
    icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
    if not os.path.exists('icon.iconset'):
        os.makedirs('icon.iconset')
    
    for size in icon_sizes:
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'icon.iconset/icon_{size}x{size}.png')
        if size <= 512:  # Save 2x version for Retina displays
            resized_2x = image.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
            resized_2x.save(f'icon.iconset/icon_{size}x{size}@2x.png')
    
    print("Icons created successfully!")

if __name__ == '__main__':
    create_icon() 