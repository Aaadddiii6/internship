import requests
from bs4 import BeautifulSoup


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
    for card in soup.select('.card'):
        name = card.select_one('.producttitle a')
        price = card.select_one('.price, .getquote')
        desc = card.select_one('.producttitle .tooltip span')
        products.append({
            'name': name.get_text(strip=True) if name else 'N/A',
            'price': price.get_text(strip=True) if price else 'N/A',
            'description': desc.get_text(strip=True) if desc else 'N/A',
            'platform': 'IndiaMART'
        })
    return products


def scrape_flipkart(url):
    """
    Placeholder for Flipkart scraper (to be implemented).
    """
    return [] 