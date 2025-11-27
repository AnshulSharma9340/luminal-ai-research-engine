# core/search.py
# Stable Google Search Integration via SerpAPI

from serpapi import GoogleSearch
import tldextract
import logging
import os
from dotenv import load_dotenv # <-- Import dotenv

# --- FIX: Ensure Keys Are Loaded Here ---
load_dotenv()

logger = logging.getLogger(__name__)

# NOTE: Key is loaded from os.environ by dotenv
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def ddg_search(query: str, max_results: int = 5) -> list:
    """
    Returns search results using SerpAPI (Google Search).
    """
    results = []
    
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY is not set. Cannot run search.")

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY, 
        "num": max_results, # Number of results
        "gl": "us", # Search region
        "lr": "lang_en" # Language filter
    }
    
    try:
        # Use the imported GoogleSearch class
        search = GoogleSearch(params) 
        data = search.get_dict()
        
        # Check for search errors from SerpAPI
        if 'error' in data:
            logger.error(f"SerpAPI Error: {data['error']}")
            return []
            
        # Extract organic results
        for r in data.get('organic_results', []):
            url = r.get('link', '')
            if url:
                domain = tldextract.extract(url).top_domain_under_public_suffix or url
                results.append({
                    "title": r.get('title', ''),
                    "url": url,
                    "snippet": r.get('snippet', 'No snippet available.'),
                    "domain": domain
                })
        
        logger.info(f"SerpAPI found {len(results)} results for '{query}'.")
        
    except Exception as e:
        logger.error(f"SerpAPI Search Failed: {e}.")
        return []

    return results