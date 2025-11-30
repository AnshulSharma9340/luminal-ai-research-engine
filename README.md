# 🚀 Luminal — AI Research Engine

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-lightgrey)](https://flask.palletsprojects.com/) [![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)]() [![SerpAPI](https://img.shields.io/badge/SerpAPI-Google%20Search-yellowgreen)](https://serpapi.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Luminal** is a Perplexity-style, high-performance AI research assistant built with Flask. It combines real-time Google search (via SerpAPI), content extraction, and Google Gemini synthesis to deliver consolidated answers with source citations, confidence scores, and an elegant Neon Glassmorphism UI.

---

## ⚡ Highlights

* **AI Core:** Gemini 2.5 Flash for multi-source consolidation and natural synthesis.
* **Real-Time Search:** SerpAPI (Google Search) for structured, high-quality results.
* **Scraping & Parsing:** `requests`, `readability-lxml`, and `BeautifulSoup` to extract clean article text.
* **Frontend:** Neon dark-theme Glassmorphism UI with real-time status stream and typewriter effects.
* **Structured Output:** Key points, Confidence scores, and clickable source citations.
* **Security:** `.env` + `.gitignore` to protect API keys.



## 🔧 Tech Stack

**Backend:** Python 3.9+, Flask
**AI:** Google Gemini (via `google-genai` SDK)
**Search:** SerpAPI (Google)
**Scraping:** `requests`, `readability-lxml`, `BeautifulSoup`
**Frontend:** HTML5, CSS (Neon Glassmorphism), JavaScript
**Optional:** Docker, systemd / Gunicorn, CI (GitHub Actions)

---

## 📁 Repository Layout

``
luminal-ai-research-engine/
├── app.py                     # Flask app and route definitions
├── requirements.txt
├── .gitignore
├── .env.example               # Example env variables (never commit .env)
├── core/
│   ├── ai_engine.py           # Gemini API calls and synthesis utilities
│   ├── search.py              # SerpAPI integration & result parsing
│   ├── scraper.py             # Fetch + extract text from URLs
│   └── research_agent.py      # Orchestrates search -> scrape -> synthesize
├── templates/
│   └── index.html             # Landing page / UI
├── static/
│   ├── css/style.css
│   └── js/app.js
└── README.md




## ⚙️ Setup — Local Development

> Use a Python virtual environment.


# 1. Clone
git clone https://github.com/AnshulSharma9340/luminal-ai-research-engine.git
cd luminal-ai-research-engine

# 2. Virtual env
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install
pip install -r requirements.txt


### Environment

Create a `.env` in the project root (do **not** commit).


# .env (example)
GEMINI_API_KEY=your_gemini_key_here
AI_PROVIDER=gemini

SERPAPI_KEY=your_serpapi_key_here
FLASK_ENV=development
FLASK_APP=app.py


Use the included `.env.example` as a template.

### Run locally


python app.py
# Visit http://127.0.0.1:5000/



## 🧭 Quick Usage

1. Open the web UI.
2. Enter a research query (e.g., *"effectiveness of CRISPR in 2024 clinical trials"*).
3. Luminal:

   * performs Google search via SerpAPI,
   * fetches top results and extracts article text,
   * sends compiled chunks to Gemini 2.5 Flash for synthesis,
   * returns structured answer with sources and confidence scores.

### Example API (internal)


POST /api/research
Content-Type: application/json

{
  "query": "latest on quantum error correction",
  "max_sources": 8
}


Response shape (simplified):


{
  "answer": "Synthesis text...",
  "key_points": ["point1", "point2"],
  "confidence": 0.87,
  "sources": [
    {"title":"Paper A", "url":"https://...", "snippet":"..."}
  ]
}




## 🏗 Architecture & Pipeline

1. **Query Reception:** Flask handles incoming queries from UI or API.
2. **Search Layer (search.py):** Calls SerpAPI for top N results and structured metadata.
3. **Scraping Layer (scraper.py):** Fetches pages, extracts readable content with `readability-lxml`.
4. **Chunking:** Clean text is split into sized chunks for the LLM.
5. **AI Layer (ai_engine.py):** Sends chunks to Gemini; receives summaries and embeddings.
6. **Consolidation (research_agent.py):** Merges summaries, computes confidence, formats citations.
7. **UI:** Live streaming of synthesis progress, final structured output.


## 🔐 Security & Privacy

* **Never** commit API keys. Use `.env` and `.gitignore`.
* Consider using a secrets manager (HashiCorp Vault, AWS Secrets Manager, Google Secret Manager) for production.
* Respect robots.txt; add polite scraping delays and rate limits.
* Provide transparency to end-users: include sources and confidence for every answer.

---

## 🧪 Testing & Validation

* Unit tests for `search.py`, `scraper.py`, and `ai_engine.py`.
* Mock SerpAPI and Gemini responses for CI.
* Example test command (pytest):


pip install -r requirements-test.txt
pytest tests/





## ♻️ Cost & Rate-limiting

* Gemini calls are billable — implement:

  * request pooling,
  * caching of previous results,
  * smaller context windows and chunk prioritization,
  * a cost cap per session and backpressure when approaching limits.

---

## 🧩 Extensibility Ideas

* Add **browser plugin** to send highlighted text into Luminal.
* Support additional search providers (Bing, custom crawlers).
* Add **retrieval-augmented generation** with vector DB (Milvus / Pinecone / Weaviate).
* Add user accounts, histories, saved reports (PDF export).
* Audit trail and provenance for each generated answer.

---

## 🤝 Contribution

Contributions are welcome! Suggested workflow:

1. Fork the repo
2. Create a branch: `feature/your-feature`
3. Add tests and update docs
4. Open a PR with a clear description and tests passing

Please follow the coding guidelines:

* Type hints where possible
* Black formatting + flake8 linting
* Small, atomic commits with meaningful messages

---

## 🛠 Troubleshooting

* **`ModuleNotFoundError` on startup**
  Ensure virtualenv is active and `pip install -r requirements.txt` succeeded.

* **Gemini auth errors**
  Confirm `GEMINI_API_KEY` in `.env`; rotate the key if needed.

* **SerpAPI limits**
  Check SerpAPI dashboard; add retries and exponential backoff.

* **Scraper returns empty text**
  Some sites block scraping. Try user-agent rotation, or rely on cached summaries.



