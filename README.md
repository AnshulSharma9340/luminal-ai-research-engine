# AI Research Engine (Perplexity-style)

Minimal Perplexity-like research assistant using Flask, simple web search scraping, HTML extraction and OpenAI summarization.

> WARNING: This is a starter-level system for learning and prototyping only. For production you should:
> - Use official search APIs (SerpAPI/Bing) instead of HTML scraping.
> - Add robust rate limiting, caching, and error handling.
> - Respect robots.txt and site TOS.

## Features
- Single-page frontend (HTML/CSS/JS)
- Flask backend with research pipeline:
  - Search (DuckDuckGo HTML endpoint)
  - Fetch & extract (readability)
  - Per-source summarization (OpenAI ChatCompletion)
  - Consolidation into final answer (OpenAI)

## Setup (local)
1. Clone this repo into `ai_research_engine/`.
2. Create and activate a venv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
