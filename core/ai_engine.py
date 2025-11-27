# core/ai_engine.py
# Stable Gemini API (Google) wrapper for summarization and consolidation. (FINAL FIX)

import os
import json
from google import genai
from typing import List
from dotenv import load_dotenv

load_dotenv()

# --- Key Loading ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("FATAL: GEMINI_API_KEY is not set in .env file.")

# Initialize client using the environment variable
client = genai.Client(api_key=GEMINI_KEY) 
# Use the best model for cost and quality
DEFAULT_MODEL = "gemini-2.5-flash" 


def _call_gemini(messages: List[dict], max_tokens: int, temp: float = 0.0, response_format: str = None) -> str:
    """Internal function to call Gemini API using correct message structure."""
    
    # Separate system instruction from user message
    system_instruction = ""
    user_message_text = ""
    
    # Process the messages to extract system instruction and user message
    for m in messages:
        if m["role"] == "system":
            system_instruction = m["content"]
        elif m["role"] == "user":
            # Assuming only one user message for our structured calls
            user_message_text = m["content"]
    
    # Configuration setup
    config_params = {"temperature": temp}
    if system_instruction:
        # Pass system instruction separately
        config_params["system_instruction"] = system_instruction
    if response_format == "json_object":
        # Pass JSON format instruction
        config_params["response_mime_type"] = "application/json"
    
    # Contents parameter must be a list of strings or Parts. 
    # We send the user message string directly inside a list, which is the simplest correct format.
    contents_list = [user_message_text] 

    resp = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=contents_list, 
        config=config_params,
    )
    
    if not resp.text:
        # Raise a clear error if the API returns no content
        raise Exception("Gemini returned empty response.")

    return resp.text.strip()


def summarize_text_piece(text: str, max_tokens=300) -> str:
    """Summarize a single long text chunk into concise notes."""
    if not text:
        return ""

    prompt = (
        "You are a helpful research assistant. Summarize the following source into a concise set of bullet points "
        "and list the most important claims (1-3 sentences each). Keep each bullet short and focus only on facts.\n\n"
        f"Source text:\n{text}\n\nSummary:"
    )
    
    try:
        messages = [{"role": "user", "content": prompt}]
        
        return _call_gemini(messages, max_tokens)
    except Exception as e:
        # Fallback to the text snippet on API failure
        return f"Error summarizing (Gemini): {str(e)[:50]}... Fallback: " + text[:600] + "..."


def consolidate_summaries(summaries: List[dict], query: str, max_tokens=600) -> dict:
    """Produces a final structured answer with citations using Gemini."""
    instruction = (
        "You are an expert research assistant. Given the user's question and multiple short source summaries, "
        "produce:\n"
        "1) A short final answer (3–6 sentences) synthesizing the evidence.\n"
        "2) A bullet list of 'Key points / evidence' with short citations like [1], [2].\n"
        "3) A short 'Confidence' note explaining whether evidence is consistent or conflicting.\n\n"
        f"User question: {query}\n\n"
        "Source summaries (numbered):\n"
    )

    text = instruction
    for i, s in enumerate(summaries, start=1):
        if "Error summarizing" not in s.get('summary', ''):
             text += (f"\n[{i}] Source: {s.get('domain') or s.get('url')}\n"
                     f"Summary:\n{s.get('summary')}\n")

    final_prompt = (text + "\n\nReturn the final result STRICTLY in one JSON object with these three keys: "
                    '{"answer": <text>, "key_points": <bullets>, "confidence": <text>}')

    try:
        messages = [
            {"role": "system", "content": "You are an accurate academic summarizer. Always output a valid JSON object."},
            {"role": "user", "content": final_prompt},
        ]
        
        content = _call_gemini(messages, max_tokens, temp=0.1, response_format="json_object")
        
        # Parsing the reliable JSON output
        parsed_content = json.loads(content)
        return {"raw": content, "model": DEFAULT_MODEL, "parsed_data": parsed_content}

    except Exception as e:
        # Fallback catches key/auth errors or JSON parse errors
        joined = f"FINAL GEMINI CALL FAILED: {str(e)}. Check API Key. FALLBACK CONTENT:\n"
        joined += "\n\n".join([f"{i+1}. {s.get('summary')}" for i, s in enumerate(summaries)])
        return {"raw": joined, "model": DEFAULT_MODEL, "parsed_data": {}}