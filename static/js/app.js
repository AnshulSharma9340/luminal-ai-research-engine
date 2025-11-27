// static/js/app.js - Final Fixed Initialization, Typewriter, Live Status Stream, and Copy Button

// --- GLOBAL VARIABLES (Initialized later) ---
let searchBtn = null;
let queryEl = null;
let resultsEl = null;

// Live Status Messages 
const statusSteps = [
    "Initializing Neural Synthesizer...",
    "Querying SerpAPI for real-time data...",
    "Scanning and filtering source URLs...",
    "Extracting clean text from web pages...",
    "Synthesizing key evidence with Gemini 2.5 Flash...",
    "Structuring final JSON response..."
];

// Typewriter function
function typeWriter(element, text, delay = 15) { // Adjusted delay for smooth typing
    let i = 0;
    element.innerHTML = '';
    const formattedText = text.replace(/\n/g, '<br>');
    
    function typing() {
        if (i < formattedText.length) {
            let char = formattedText.charAt(i);
            
            // Handle HTML tags (like <ul>, <li>, <b>, <i>) correctly to avoid broken rendering
            if (char === '<') {
                let tagEnd = formattedText.indexOf('>', i);
                if (tagEnd !== -1) {
                    element.innerHTML += formattedText.substring(i, tagEnd + 1);
                    i = tagEnd + 1;
                    return setTimeout(typing, delay);
                }
            }
            
            element.innerHTML += char;
            i++;
            setTimeout(typing, delay);
        }
    }
    typing();
}

// Copy Button Logic (Accessible globally via window)
window.copyAnswer = function(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const textToCopy = element.textContent || element.innerText;
    
    const tempTextArea = document.createElement('textarea');
    tempTextArea.value = textToCopy;
    document.body.appendChild(tempTextArea);
    tempTextArea.select();
    document.execCommand('copy');
    document.body.removeChild(tempTextArea);
    
    alert('Answer copied to clipboard!');
};

// Live Status Stream Function
function startStatusStream(statusElement) {
    let step = 0;
    statusElement.textContent = statusSteps[0];

    const intervalId = setInterval(() => {
        step = (step + 1) % statusSteps.length;
        statusElement.textContent = statusSteps[step];
    }, 3000); 
    
    return intervalId;
}


// static/js/app.js (Inside the doSearch function)

async function doSearch() {
  if (!queryEl || !searchBtn) return console.error("Initialization failed: Elements not found.");

  const query = queryEl.value.trim();
  const maxResults = document.getElementById('max_results').value;
  if (!query) return alert('Please enter a query');
  
  // 1. Setup loading state with status area (Immediate UI update)
  resultsEl.classList.remove('visible'); 
  searchBtn.disabled = true;

  resultsEl.innerHTML = `
    <div class="result-card loading-card">
        <div class="loading-spinner"></div>
        <p id="live-status">Initializing Neural Synthesizer...</p>
    </div>`;
  
  // FIX: Force browser to render the loading state immediately 
  // before starting the long network request.
  await new Promise(resolve => setTimeout(resolve, 50)); // Wait 50ms for UI rendering

  const statusElement = document.getElementById('live-status');
  const statusInterval = startStatusStream(statusElement); 

  try {
    const resp = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, max_results: maxResults })
    });
    const data = await resp.json();
    clearInterval(statusInterval); // Stop status animation on response

    if (!resp.ok || data.error) {
      // ... (Error handling remains the same)
      resultsEl.innerHTML = `<div class="result-card"><p class="small" style="color:#f87171">Error: ${data.error || 'Unknown API Error'}</p><p class="small">Please verify your **GEMINI_API_KEY** and **SERPAPI_KEY** are valid, and ensure your code is saved.</p></div>`;
      resultsEl.classList.add('visible');
      return;
    }
    renderResult(data);
    resultsEl.classList.add('visible'); 

  } catch (err) {
    clearInterval(statusInterval);
    resultsEl.innerHTML = `<div class="result-card"><p class="small" style="color:#f87171">Network error: ${err.message}</p></div>`;
    resultsEl.classList.add('visible');
  } finally {
    searchBtn.disabled = false;
  }
}


function renderResult(data) {
  resultsEl.innerHTML = '';
  const parsed = data.parsed_data || {};

  let answerContent = parsed.answer || data.answer || 'Analysis complete. No synthesized answer could be generated from available sources.';
  let keyPointsContent = parsed.key_points || 'No key points extracted.';
  let confidenceContent = parsed.confidence || 'Confidence not determined.';
  
  const final = document.createElement('div');
  final.className = 'result-card';
  
  // Set ID for the copy button to target
  final.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.15); padding-bottom: 12px; margin-top: 0;">
        <h3 style="margin: 0; border-bottom: none;"><i class="fas fa-microchip"></i> Final Synthesized Answer</h3>
        <button onclick="copyAnswer('answer-output')" class="copy-button"><i class="fas fa-copy"></i> Copy</button>
    </div>
    <div id="answer-output" class="result-summary typing-area" style="margin-top: 15px;"></div>

    <h4 style="margin-top: 20px;"><i class="fas fa-list-ul"></i> Key Points & Evidence</h4>
    <div class="result-summary">
        ${(Array.isArray(keyPointsContent) ? `<ul>${keyPointsContent.map(p => `<li>${escapeHtml(p)}</li>`).join('')}</ul>` : escapeHtml(keyPointsContent))}
    </div>

    <h4 style="margin-top: 20px;"><i class="fas fa-shield-alt"></i> Confidence Score</h4>
    <p class="small" style="color: ${confidenceContent.toLowerCase().includes('consistent') ? '#4ade80' : confidenceContent.toLowerCase().includes('conflicting') ? '#f87171' : 'var(--text-secondary)'}">${escapeHtml(confidenceContent)}</p>

    <div class="small" style="margin-top:15px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
        Model used: ${data.model || 'N/A'} • Generated at: ${new Date().toLocaleString()}
    </div>`;
  resultsEl.appendChild(final);
  
  // Apply the typewriter effect to the main answer
  typeWriter(final.querySelector('#answer-output'), answerContent, 20); 

  // 2. Sources Card (injects source list below the final answer)
  if (data.sources && data.sources.length) {
    const srcCard = document.createElement('div');
    srcCard.className = 'result-card';
    srcCard.innerHTML = `<h4><i class="fas fa-book"></i> Sources Used (${data.sources.length})</h4>`;
    const list = document.createElement('div');
    list.className = 'source-list';
    data.sources.forEach((s, index) => {
      const item = document.createElement('div');
      item.className = 'source-item';
      item.innerHTML = `<div style="font-size: 14px;"><a class="cite" href="${s.url}" target="_blank" rel="noopener noreferrer">**[${index + 1}]** ${escapeHtml(s.title || s.url)}</a></div>
        <div class="small">${escapeHtml(s.domain)} • ${escapeHtml(s.snippet || 'No snippet available.')}</div>`;
      list.appendChild(item);
    });
    srcCard.appendChild(list);
    resultsEl.appendChild(srcCard);
  }
}

function escapeHtml(unsafe) {
  if (!unsafe && unsafe !== 0) return '';
  return String(unsafe)
    .replaceAll('&', "&amp;")
    .replaceAll('<', "&lt;")
    .replaceAll('>', "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


// --- FINAL INITIALIZATION FIX: Attach listeners after DOM is loaded ---
document.addEventListener('DOMContentLoaded', () => {
    // Initialize elements here
    searchBtn = document.getElementById('search');
    queryEl = document.getElementById('query');
    resultsEl = document.getElementById('results');
    
    if (searchBtn && queryEl) {
        // Attach event listener to the button click
        searchBtn.addEventListener('click', doSearch);
        
        // Attach event listener for Ctrl+Enter
        queryEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault(); // Prevent default newline in textarea
                doSearch();
            }
        });
    } else {
        console.error("Initialization failed: Search button or query element not found in DOM.");
    }
});