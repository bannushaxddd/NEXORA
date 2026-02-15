from fastapi import FastAPI, Query
from src.indexing.crawler import load_documents

app = FastAPI(title="NEXORA Search Engine")

# Load documents once at startup
documents = load_documents()

@app.get("/")
def health():
    """Health check endpoint"""
    return {"status": "NEXORA running"}

@app.get("/search")
def search(q: str = Query(..., description="Search query")):
    """Simple search over loaded documents"""
    results = []

    query_lower = q.lower()
    for doc_id, text in documents.items():
        if query_lower in text.lower():
            results.append({
                "doc_id": doc_id,
                "preview": text[:200]  # first 200 chars
            })

    return {
        "query": q,
        "results": results[:10],  # max 10 results
        "total_results": len(results)
    }
