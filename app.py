import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from utils.poster_maker import generate_poster
import sqlite3
from werkzeug.utils import secure_filename
from scraper import scrape_indiamart

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
        if competitor_url and 'indiamart' in competitor_url:
            try:
                products = scrape_indiamart(competitor_url)
                if not products:
                    scrape_message = 'No products found or page structure changed.'
            except Exception as e:
                scrape_message = f'Error scraping IndiaMART: {e}'
        else:
            scrape_message = 'Only IndiaMART URLs are supported for now.'
    return render_template('scraper.html', products=products, scrape_message=scrape_message)

if __name__ == '__main__':
    app.run(debug=True) 