import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from utils.poster_maker import generate_poster
import sqlite3
from werkzeug.utils import secure_filename

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
def index():
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
        # Generate poster and caption
        poster_filename, caption = generate_poster(product_name, price, description, image_path)
        # Save to DB
        conn = get_db_connection()
        conn.execute('INSERT INTO posters (product_name, price, description, image_filename, poster_filename, caption) VALUES (?, ?, ?, ?, ?, ?)',
                     (product_name, price, description, image_filename, poster_filename, caption))
        conn.commit()
        conn.close()
        return render_template('index.html', poster_url=url_for('static', filename=f'posters/{poster_filename}'), caption=caption)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 