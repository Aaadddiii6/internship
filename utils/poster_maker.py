from PIL import Image, ImageDraw, ImageFont
import os
import uuid

def generate_poster(product_name, price, description, image_path, font_path=None):
    """
    Generates a poster by pasting the product image and drawing text on a background template.
    - product_name: string
    - price: string
    - description: string
    - image_path: path to the uploaded product image
    - font_path: path to a .ttf font file (optional)
    Returns: (poster_filename, caption)
    """
    # Load background template
    background_path = os.path.join('static', 'template.png')
    bg = Image.open(background_path).convert('RGBA')
    W, H = bg.size

    # Load and resize product image
    if image_path and os.path.exists(image_path):
        product_img = Image.open(image_path).convert('RGBA')
        product_img = product_img.resize((240, 250
        ))
        bg.paste(product_img, (190, 187), product_img)

    # Prepare to draw text
    draw = ImageDraw.Draw(bg)
    if font_path and os.path.exists(font_path):
        font_title = ImageFont.truetype(font_path, 48)
        font_price = ImageFont.truetype(font_path, 40)
        font_desc = ImageFont.truetype(font_path, 32)
    else:
        font_title = font_price = font_desc = ImageFont.load_default()

    # Draw text at specified positions
    draw.text((313, 75), product_name, font=font_title, fill=(0,0,0,255))
    draw.text((487, 320), price, font=font_price, fill=(34,139,34,255))
    draw.text((313, 530), description, font=font_desc, fill=(0,0,0,255))

    # Save the final poster
    poster_filename = f"poster_{uuid.uuid4().hex[:8]}.png"
    poster_path = os.path.join('static/posters', poster_filename)
    bg.convert('RGB').save(poster_path)

    # Generate a simple caption
    caption = f"Check out our {product_name} for just {price}! {description[:50]}..."
    return poster_filename, caption 