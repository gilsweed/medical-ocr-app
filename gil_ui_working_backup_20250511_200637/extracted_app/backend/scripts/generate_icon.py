from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    # Create a new image with a white background
    size = 1024
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a rounded rectangle for the document
    doc_color = (41, 128, 185)  # Blue color
    doc_padding = size // 8
    doc_rect = [
        doc_padding,
        doc_padding,
        size - doc_padding,
        size - doc_padding
    ]
    draw.rounded_rectangle(doc_rect, radius=size//16, fill=doc_color)
    
    # Draw scan lines
    line_color = (255, 255, 255, 180)  # Semi-transparent white
    line_spacing = size // 12
    for y in range(doc_padding * 2, size - doc_padding * 2, line_spacing):
        draw.line([(doc_padding * 2, y), (size - doc_padding * 2, y)], 
                 fill=line_color, width=2)
    
    # Draw OCR text symbol
    text_color = (255, 255, 255)
    try:
        # Try to use a system font
        font = ImageFont.truetype("Arial", size=size//4)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "OCR"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_position = (
        (size - text_width) // 2,
        (size - text_height) // 2
    )
    
    draw.text(text_position, text, fill=text_color, font=font)
    
    # Save the icon in different sizes
    icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    os.makedirs(icon_dir, exist_ok=True)
    
    # Save PNG version
    png_path = os.path.join(icon_dir, 'icon.png')
    image.save(png_path, 'PNG')
    
    # Save different sizes
    for icon_size in icon_sizes:
        resized = image.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        resized_path = os.path.join(icon_dir, f'icon_{icon_size}.png')
        resized.save(resized_path, 'PNG')
    
    print(f"Icon generated successfully at {png_path}")
    return png_path

if __name__ == '__main__':
    create_app_icon() 