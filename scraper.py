import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import traceback


def scrape_indiamart(url):
    """
    Scrape product info from an IndiaMART search results page.
    Returns a list of dicts: {name, price, description, platform}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    products = []
    for card in soup.select('div.card'):
        name_tag = card.select_one('div.producttitle a.cardlinks')
        price_tag = card.select_one('p.price, p.getquote')
        desc_tag = card.select_one('div.producttitle a.cardlinks')
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'
        price = price_tag.get_text(strip=True) if price_tag else 'N/A'
        description = desc_tag.get_text(strip=True) if desc_tag else 'N/A'
        products.append({
            'name': name,
            'price': price,
            'description': description,
            'platform': 'IndiaMART'
        })
        if len(products) >= 10:
            break
    if not products:
        print('[DEBUG] IndiaMART: No products found. Check selectors or anti-bot.')
    return products


def parse_cookies(cookie_str):
    """Parse a cookie string (as from browser) into a dict."""
    cookies = {}
    if cookie_str:
        for pair in cookie_str.split(';'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                cookies[k.strip()] = v.strip()
    return cookies


def scrape_flipkart(url, cookie_str=None, max_retries=3):
    """
    Scrape product info from a Flipkart search results page.
    Returns a dict: {'products': [...], 'error': ...}
    Each product includes 'product_url' for review extraction.
    """
    import time
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    cookies = parse_cookies(cookie_str) if cookie_str else None
    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            print("[DEBUG] Flipkart title:", soup.title)
            print("[DEBUG] Flipkart status code:", resp.status_code)
            # Detect anti-bot/"rush" page
            if soup.find(string=lambda s: isinstance(s, str) and ("Lot of rush" in s or "Retry in" in s)):
                last_error = "Blocked by Flipkart anti-bot. Try again later or use browser cookies."
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            products = []
            cards = soup.select('a.CGtC98')
            if not cards:
                print('[WARNING] Flipkart: No product cards found with selector a.CGtC98. HTML snippet:', resp.text[:500])
            for card in cards:
                try:
                    name = card.find('div', class_='KzDlHZ')
                    price = card.find('div', class_='Nx9bqj _4b5DiR')
                    if not price:
                        price = card.find('div', class_='_30jeq3')
                    desc_ul = card.find('ul', class_='G4BRas')
                    description = None
                    if desc_ul and isinstance(desc_ul, Tag):
                        description = ' | '.join(li.get_text(strip=True) for li in desc_ul.find_all('li'))
                    href = card.get('href')
                    product_url = f'https://www.flipkart.com{href}' if isinstance(href, str) and href.startswith('/') else href
                    products.append({
                        'name': name.get_text(strip=True) if name else 'N/A',
                        'price': price.get_text(strip=True) if price else 'N/A',
                        'description': description if description else 'N/A',
                        'platform': 'Flipkart',
                        'product_url': product_url
                    })
                    if len(products) >= 10:
                        break
                except Exception as parse_e:
                    print(f"[ERROR] Flipkart product parsing failed: {parse_e}")
                    traceback.print_exc()
            if products:
                return {'products': products, 'error': None}
            print('[DEBUG] Flipkart: No products found. HTML snippet:', resp.text[:500])
            last_error = "No products found. Flipkart may have changed their layout or blocked the request."
        except Exception as e:
            print(f"[ERROR] Flipkart scraping failed: {e}")
            traceback.print_exc()
            last_error = str(e)
            time.sleep(2 ** attempt)
    return {'products': [], 'error': last_error}


def scrape_amazon(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    products = []
    for card in soup.select('div.s-result-item'):
        name = card.select_one('span.a-size-medium.a-color-base.a-text-normal')
        price = card.select_one('span.a-price-whole')
        desc = card.select_one('div.a-row.a-size-base.a-color-secondary, div.a-row.a-size-base.a-color-base')
        link = card.select_one('a.a-link-normal.a-text-normal, a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
        href = link.get('href') if link else None
        product_url = f'https://www.amazon.in{href}' if isinstance(href, str) and href.startswith('/') else href
        if not name:
            continue
        products.append({
            'name': name.get_text(strip=True),
            'price': price.get_text(strip=True) if price else 'N/A',
            'description': desc.get_text(" ", strip=True) if desc else 'N/A',
            'platform': 'Amazon',
            'product_url': product_url
        })
        if len(products) >= 10:
            break
    return products 