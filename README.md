# 🛍️ Market Mint

**Market Mint** is a web-based platform that allows users to **generate stylish product posters** using simple form inputs. It also features a basic **web scraping tool** to fetch product info from IndiaMART. Perfect for small business owners, marketers, or online sellers who need quick poster designs without graphic tools.

---

## 📸 Features

- 🎨 Product Poster Generator  
  Enter product name, price, description, and upload an image to generate a clean, downloadable product poster.

- 🔎 Web Scraper  
  Scrape product info from IndiaMART to save time filling in details.

- 📱 Responsive UI  
  Mobile-friendly layout with neatly styled cards and components.

- 🤖 AI Poster Generator (Upcoming)  
  Future plans to include integration with Hugging Face for automatic poster creation.

---

## 🧰 Tech Stack

- **Frontend**: HTML5, CSS3, Jinja2 (template engine)  
- **Backend**: Python, Flask  
- **Libraries/Tools**:
  - `BeautifulSoup` — Web scraping
  - `Requests` — API & web data
  - `Pillow (PIL)` — Poster rendering (if applicable)

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/market-mint.git
cd market-mint
```
Set up virtual environment (optional)
bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate


market-mint/
│
├── static/
│   ├── posters/             # Generated posters & background image
│   ├── fonts/               # Varsity Regular font
│
├── templates/
│   ├── base.html            # Layout & navbar
│   ├── poster.html          # Poster generator UI
│   ├── scraper.html         # Scraper UI
│
├── app.py                   # Flask route handlers
├── scraper.py               # Web scraping logic
├── requirements.txt
├── README.md


