import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from utils.poster_maker import generate_poster, extract_reviews, analyze_sentiment
import sqlite3
from werkzeug.utils import secure_filename
from scraper import scrape_indiamart, scrape_flipkart, scrape_amazon

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['POSTER_FOLDER'] = 'static/posters'
app.config['DATABASE'] = 'poster_maker.db'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['POSTER_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS posters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        price TEXT,
        description TEXT,
        image_filename TEXT,
        poster_filename TEXT,
        caption TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
@app.route('/poster', methods=['GET', 'POST'])
def poster():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)
        else:
            image_filename = None
            image_path = None
        poster_filename, caption = generate_poster(product_name, price, description, image_path)
        conn = get_db_connection()
        conn.execute('INSERT INTO posters (product_name, price, description, image_filename, poster_filename, caption) VALUES (?, ?, ?, ?, ?, ?)',
                     (product_name, price, description, image_filename, poster_filename, caption))
        conn.commit()
        conn.close()
        return render_template('poster.html', poster_url=url_for('static', filename=f'posters/{poster_filename}'), caption=caption)
    return render_template('poster.html')

@app.route('/scraper', methods=['GET', 'POST'])
def scraper():
    products = []
    scrape_message = None
    if request.method == 'POST':
        competitor_url = request.form.get('competitor_url')
        if competitor_url:
            try:
                if 'indiamart' in competitor_url:
                    products = scrape_indiamart(competitor_url)
                elif 'flipkart' in competitor_url:
                    result = scrape_flipkart(competitor_url)
                    if isinstance(result, dict):
                        products = result.get('products', [])
                        if result.get('error'):
                            scrape_message = result['error']
                    else:
                        products = result
                elif 'amazon' in competitor_url:
                    products = scrape_amazon(competitor_url)
                else:
                    scrape_message = 'Only IndiaMART, Flipkart, and Amazon URLs are supported for now.'
                # For each product, extract reviews and compute sentiment
                for idx, p in enumerate(products):
                    product_url = p.get('product_url')
                    platform = p.get('platform')
                    try:
                        reviews = extract_reviews(product_url, platform)
                        used_mock = False
                        if not reviews and platform and platform.lower() in ('flipkart', 'amazon'):
                            print(f"[DEBUG] No real reviews found for {p.get('name')}, using mock reviews.")
                            reviews = extract_reviews(None, 'indiamart')
                            used_mock = True
                        else:
                            print(f"[DEBUG] Using real reviews for {p.get('name')}, count: {len(reviews)}")
                        sentiment, _ = analyze_sentiment(reviews)
                        if isinstance(sentiment, float):
                            p['sentiment'] = {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'avg': sentiment}
                        else:
                            p['sentiment'] = sentiment
                        print(f"[DEBUG] {p.get('name')} | Sentiment: {p['sentiment']} | Source: {'mock' if used_mock else 'real'}")
                    except Exception as e:
                        print(f"[ERROR] Sentiment extraction failed for {p.get('name')}: {e}")
                        p['sentiment'] = {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'avg': 0.0}
                if not products and not scrape_message:
                    scrape_message = 'No products found or page structure changed.'
            except Exception as e:
                scrape_message = f'Error scraping: {e}'
        else:
            scrape_message = 'Please enter a valid URL.'
    return render_template('scraper.html', products=products, scrape_message=scrape_message)

if __name__ == '__main__':
    app.run(debug=True) 