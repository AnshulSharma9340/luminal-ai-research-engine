# test_search.py
import os
import sys
# Add project root to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
from core.search import ddg_search

print("--- Testing DDGS Search ---")
results = ddg_search("future of AI in 2026", max_results=3)

if results:
    print(f"Success! Found {len(results)} results:")
    for r in results:
        print(f"- {r.get('title')} ({r.get('domain')})")
else:
    print("Failure: DDGS returned no results.")