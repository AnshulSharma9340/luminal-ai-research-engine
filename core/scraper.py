# core/scraper.py
# Fetch page and extract main content using readability-lxml + BeautifulSoup fallback
import requests
from readability import Document
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def fetch_html(url, timeout=15, retries=2):
    """Fetch HTML content from URL with optional retries."""
    for _ in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException:
            # Log this error if using logging, but for now, just wait and retry
            time.sleep(1)
            continue
    return None

def extract_text_from_html(html):
    """Extract meaningful text from HTML using readability-lxml and fallback."""
    if not html:
        return ""

    # First try readability-lxml (Best for clean articles)
    try:
        doc = Document(html)
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, 'lxml') # Use lxml parser
        texts = [node.get_text(strip=True) for node in soup.find_all(['h1','h2','h3','p','li']) if node.get_text(strip=True)]
        if texts:
            return "\n\n".join(texts)
    except Exception:
        pass

    # Fallback: simple text extraction from full page (Good for all pages)
    try:
        soup = BeautifulSoup(html, 'lxml')
        # Remove script, style, header, footer, nav elements to clean up
        for element in soup(["script", "style", "header", "footer", "nav", "aside", "form", "button"]):
            element.decompose()
            
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        if len(paragraphs) > 5: # Only return if we found a decent amount of text
            return "\n\n".join(paragraphs)
        
        # Final fallback: just get all visible text
        return soup.get_text(separator='\n', strip=True)

    except Exception:
        return ""

def domain_from_url(url):
    """Return domain name from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return url