# core/research_agent.py
# Orchestrates the search, scraping, and AI summarization pipeline. (Updated for Gemini)

from .search import ddg_search
from .scraper import fetch_html, extract_text_from_html, domain_from_url
from .ai_engine import summarize_text_piece, consolidate_summaries, DEFAULT_MODEL
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

class ResearchAgent:
    """
    The main agent responsible for running the Perplexity-style research pipeline.
    """
    def __init__(self):
        self.fetch_workers = 5

    def fetch_and_summarize(self, result):
        """
        Fetches HTML, extracts clean text, and uses AI to summarize the piece.
        """
        url = result.get('url')
        logger.info(f"-> Fetching URL: {url}")
        
        # 1. Fetch HTML (with retries)
        html = fetch_html(url)
        if not html:
            logger.warning(f"Failed to fetch content from {url}")
            return None
        
        # 2. Extract clean text
        text = extract_text_from_html(html)
        # 100 characters minimum to avoid junk text
        if not text or len(text) < 100: 
            logger.warning(f"Extracted too little text from {url}. Skipping.")
            return None

        # Prepare snippet and domain information
        snippet = (text[:400] + '...') if len(text) > 400 else text
        domain = result.get('domain') or domain_from_url(url)
        
        # 3. AI Summarization (Gemini)
        try:
            summary = summarize_text_piece(text, max_tokens=250)
            logger.info(f"-> Successfully summarized content from {domain}")
        except Exception as e:
            logger.error(f"AI Summarization failed for {domain}: {e}")
            summary = "Error summarizing content."

        return {
            "url": url,
            "domain": domain,
            "title": result.get('title'),
            "snippet": snippet,
            "summary": summary
        }

    def run(self, query, max_results=5):
        logger.info(f"--- Starting research for query: {query} ---")
        
        # 1. Search (using core/search.py with SerpAPI)
        search_results = ddg_search(query, max_results=max_results)
        
        if not search_results:
            return {"answer": "Search failed or returned no results. Please check your SerpAPI key and query.", 
                    "sources": [], "per_source": [], "model": None, "error": "No search results"}

        # FIX: Filter out known problematic domains (like LinkedIn) that block basic scraping
        filtered_results = []
        for r in search_results:
            if 'linkedin.com' not in r.get('url', '').lower():
                filtered_results.append(r)
            else:
                logger.warning(f"Skipping LinkedIn URL due to scraping blocks: {r.get('url')}")
        
        search_results = filtered_results 

        if not search_results:
            return {"answer": "Search results were found, but all usable links were filtered out (e.g., LinkedIn). Try a different query.", 
                    "sources": [], "per_source": [], "model": None, "error": "No usable results"}
        
        # 2. Fetch and summarize in parallel
        per_source = []
        with ThreadPoolExecutor(max_workers=self.fetch_workers) as ex:
            futures = {ex.submit(self.fetch_and_summarize, r): r for r in search_results}
            
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    if res: # Only append if fetching and summarizing was successful
                        per_source.append(res)
                except Exception as e:
                    logger.error(f"Thread failed during fetch/summarize: {e}")

        # If no source provided usable content, return gracefully
        if not per_source:
             return {"answer": "Could not extract usable content from any sources. Try a broader search or check scraper logs.", 
                    "sources": [], "per_source": [], "model": None, "error": "No useful content extracted"}
        
        # 3. Consolidate (using core/ai_engine.py with Gemini)
        logger.info(f"-> Consolidating {len(per_source)} source summaries...")
        consolidated = consolidate_summaries(per_source, query)
        
        final_answer = consolidated.get('parsed_data', {}).get('answer') or consolidated.get('raw')
        
        # Prepare final structured output
        return {
            "query": query,
            "answer": final_answer,
            "model": consolidated.get('model') or DEFAULT_MODEL, # Use the model name from ai_engine
            "sources": [{"url": s["url"], "title": s.get("title") or s.get("domain"), "domain": s.get("domain"), "snippet": s.get("snippet")} for s in per_source],
            "per_source": per_source,
            "parsed_data": consolidated.get('parsed_data', {}) # Pass structured data to frontend
        }