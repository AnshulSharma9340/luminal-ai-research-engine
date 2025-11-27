# app.py
from flask import Flask, render_template, request, jsonify
from core.research_agent import ResearchAgent
from dotenv import load_dotenv
import logging
import os

# Load .env file at the start
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
agent = ResearchAgent()

# Basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

# app.py (Modified api_search route for Gemini)
@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    max_results = int(data.get('max_results', 5))
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    try:
        result = agent.run(query, max_results=max_results)
        
        if not result.get('sources') and not result.get('answer'):
            return jsonify({'error': 'Search successful but could not find/extract useful information from any page.'}), 500

        return jsonify(result)
        
    except ValueError as e:
        # Catch the API Key missing error (updated for Gemini)
        if "GEMINI_API_KEY is missing or invalid" in str(e):
             app.logger.error("FATAL: GEMINI API Key is missing.")
             return jsonify({'error': 'FATAL API ERROR: GEMINI API Key is missing or invalid. Check your .env file.'}), 500
        else:
            app.logger.exception("Search failed due to internal ValueError")
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.exception("Internal search failure")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)