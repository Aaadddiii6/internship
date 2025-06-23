from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import requests
from bs4 import BeautifulSoup
import random

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

def extract_reviews(product_url, platform):
    """
    Extract up to 20 reviews for a product from the given URL and platform.
    For IndiaMART, returns mock reviews. For Flipkart/Amazon, tries real reviews, else uses 20 random mock reviews.
    Returns a list of review texts.
    """
    # 36 positive, 18 negative, 6 neutral reviews (total 60)
    mock_reviews = [
        # Positive (36)
        "Amazing quality for this price range!",
        "Absolutely love it, buying another one soon!",
        "Battery backup is outstanding!",
        "Incredible features. Exceeded expectations!",
        "Feels smooth and premium.",
        "Perfect for daily use!",
        "Happy with the purchase, worth every rupee.",
        "Build quality feels sturdy and reliable.",
        "Five stars from me. Loved it!",
        "Very stylish and well-designed.",
        "Meets all my expectations. Solid product.",
        "Looks fancy, performs even better!",
        "Packaging was decent. Product worked fine.",
        "Great buy. Impressed by the build!",
        "Works perfectly out of the box.",
        "Feels premium, and battery lasts long.",
        "All features working smoothly.",
        "Excellent customer support!",
        "Surprisingly good for the price.",
        "Highly recommend it to anyone!",
        "Totally satisfied with the performance.",
        "Works like a charm, no issues at all.",
        "This is exactly what I was looking for.",
        "Sound quality is above average.",
        "Fast charging and long battery life!",
        "Easy to use and setup.",
        "Responsive and smooth interface.",
        "Great value for money.",
        "Impressive camera quality.",
        "Lightweight and portable.",
        "Customer support was very helpful.",
        "Stylish design and comfortable to hold.",
        "Quick delivery and well packaged.",
        "Exceeded my expectations!",
        "Would recommend to friends and family.",
        "Affordable and reliable.",
        # Negative (18)
        "Didn't last more than a week, complete waste.",
        "Too fragile. Broke with minimal use.",
        "Cheap materials used, not recommended.",
        "Arrived damaged. Had to return it.",
        "Delivery was late and box was open.",
        "Started malfunctioning in just 3 days.",
        "Sound quality is below average.",
        "Useless after one update. Trash.",
        "Waste of money, regret buying.",
        "Support team was unresponsive.",
        "Horrible experience. Do not recommend.",
        "Laggy performance. Bad for multitasking.",
        "The app keeps crashing constantly.",
        "Item was missing from the box.",
        "Unnecessarily overpriced and underperforms.",
        "The cable broke in two days.",
        "Charging takes forever. Very annoying.",
        "Poor build and flimsy finish.",
        # Neutral (6)
        "Product is okay, nothing exceptional.",
        "Not good, not bad. Just average.",
        "Satisfactory, does what it's supposed to.",
        "Okayish performance, but still usable.",
        "Functionality is okay, feels outdated though.",
        "Just an average product, don't expect much."
    ]
    if platform and platform.lower() == 'indiamart':
        return random.sample(mock_reviews, 20)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        if platform and platform.lower() == 'flipkart':
            resp = requests.get(product_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            reviews = [div.get_text(strip=True) for div in soup.select('div.t-ZTKy')]
            reviews = [r for r in reviews if len(r) > 10]
            if reviews:
                return reviews[:20]
        elif platform and platform.lower() == 'amazon':
            resp = requests.get(product_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            reviews = [span.get_text(strip=True) for span in soup.select('span[data-hook="review-body"]')]
            reviews = [r for r in reviews if len(r) > 10]
            if reviews:
                return reviews[:20]
    except Exception as e:
        print(f"Review extraction error for {platform}: {e}")
    # Fallback: 20 random mock reviews
    return random.sample(mock_reviews, 20)

def analyze_sentiment(reviews):
    """
    Given a list of review texts, return the percentage of positive, negative, and neutral reviews.
    Uses TextBlob for sentiment analysis.
    Returns a dict: {'positive': x, 'negative': y, 'neutral': z, 'avg': avg_polarity}
    """
    from textblob import TextBlob
    if not reviews:
        return {'positive': 0, 'negative': 0, 'neutral': 0, 'avg': 0.0}, []
    sentiments = []
    pos = neg = neu = 0
    for review in reviews:
        blob = TextBlob(review)
        polarity = blob.sentiment.polarity
        sentiments.append((review, polarity))
        if polarity >= 0.2:
            pos += 1
        elif polarity <= -0.2:
            neg += 1
        else:
            neu += 1
    total = len(reviews)
    avg_polarity = sum(p for _, p in sentiments) / total
    return {
        'positive': pos / total,
        'negative': neg / total,
        'neutral': neu / total,
        'avg': avg_polarity
    }, sentiments
