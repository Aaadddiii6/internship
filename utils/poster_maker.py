from PIL import Image, ImageDraw, ImageFont
import os
import uuid

def generate_poster(product_name, price, description, image_path, font_path=None):
    """
    Generates a poster with product image, centered title and description in transparent boxes.
    Handles text wrapping, centering, and font shrinking.
    """
    # Load background template
    background_path = os.path.join('static', 'template.png')
    bg = Image.open(background_path).convert('RGBA')
    W, H = bg.size

    # Load and resize product image
    if image_path and os.path.exists(image_path):
        product_img = Image.open(image_path).convert('RGBA')
        product_img = product_img.resize((240, 250))
        bg.paste(product_img, (190, 187), product_img)

    draw = ImageDraw.Draw(bg, 'RGBA')

    # Font paths
    title_font_path = os.path.join("static", "fonts", "Persona Aura.otf")
    price_font_path = os.path.join("static", "fonts", "Neka Laurent (Demo_Font).ttf")
    desc_font_path  = os.path.join("static", "fonts", "CreatoDisplay-Bold.otf")

    # Load fonts (default fallback)
    try:
        font_title_base = ImageFont.truetype(title_font_path, 50)
        font_price = ImageFont.truetype(price_font_path, 29)
        font_desc_base = ImageFont.truetype(desc_font_path, 26)
    except:
        font_title_base = font_price = font_desc_base = ImageFont.load_default()

    # Utility function: wrap, center, limit lines, shrink font if needed
    def draw_wrapped_text(draw, text, box, base_font, max_lines=2, fill=(255, 255, 255, 255)):
        x, y, w, h = box
        font = base_font
        while True:
            words = text.split()
            lines, line = [], ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_w = draw.textbbox((0, 0), test_line, font=font)[2]
                if test_w <= w:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)

            if len(lines) <= max_lines:
                break
            else:
                # Shrink font
                size = font.size - 1
                if size < 10:
                    lines = lines[:max_lines]
                    break
                font = ImageFont.truetype(font.path, size)

        total_height = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] for l in lines)
        y_start = y + (h - total_height) // 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
            draw.text((x + (w - line_w) // 2, y_start), line, font=font, fill=fill)
            y_start += line_h

    # --- TITLE ---
    title_box = (138, 40, 350, 70)

    draw_wrapped_text(draw, product_name, title_box, font_title_base, max_lines=2, fill=(255, 255, 0, 255))

    # --- PRICE ---
    draw.text((440, 300), price, font=font_price, fill=(34, 139, 34, 255))

    # --- DESCRIPTION ---
    desc_box = (0, 514, 626, 100)
    draw_wrapped_text(draw, description, desc_box, font_desc_base, max_lines=2, fill=(255, 255, 255, 255))

    # Save poster
    poster_filename = f"poster_{uuid.uuid4().hex[:8]}.png"
    poster_path = os.path.join('static/posters', poster_filename)
    os.makedirs(os.path.dirname(poster_path), exist_ok=True)
    bg.convert('RGB').save(poster_path)

    # Caption
    caption = f"Check out our {product_name} for just {price}! {description[:50]}..."
    return poster_filename, caption
