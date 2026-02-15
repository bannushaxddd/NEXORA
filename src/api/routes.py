from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from src.indexing.crawler import load_documents
from src.search.engine import SearchEngine
from src.search.cache import cache
from src.logger import logger, setup_logging
from src.config import settings


# Global search engine instance
search_engine: SearchEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global search_engine
    
    # Startup
    setup_logging(settings.log_level)
    logger.info("nexora_starting")
    
    # Connect to cache
    await cache.connect()
    
    # Load and index documents
    documents = load_documents()
    logger.info("documents_loaded", count=len(documents))
    
    # Initialize search engine with BM25
    search_engine = SearchEngine(documents)
    logger.info("search_engine_initialized", 
                num_docs=search_engine.num_docs,
                avg_doc_len=search_engine.avg_doc_len)
    
    print("\n" + "=" * 60)
    print("  ✅ NEXORA Search Engine Ready!")
    print("=" * 60)
    print(f"  📚 Indexed {len(documents)} documents")
    print(f"  🔍 BM25 algorithm with k1={settings.bm25_k1}, b={settings.bm25_b}")
    print(f"  🌐 Search UI: http://localhost:{settings.api_port}/")
    print(f"  📖 API Docs: http://localhost:{settings.api_port}/docs")
    print(f"  🧪 Try: http://localhost:{settings.api_port}/search?q=python&top_k=3")
    print("=" * 60 + "\n")
    
    yield
    
    # Shutdown
    await cache.disconnect()
    logger.info("nexora_shutdown")


# Create FastAPI app
app = FastAPI(
    title="NEXORA Search Engine",
    description="Production-grade search engine with BM25 ranking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Path to static search UI (project root / static / index.html)
_STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
_INDEX_HTML = _STATIC_DIR / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the NEXORA search UI"""
    if _INDEX_HTML.exists():
        return HTMLResponse(content=_INDEX_HTML.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>NEXORA</h1><p>Static UI not found. Check /health and /docs.</p>", status_code=404)


@app.get("/health")
async def health():
    """Health check endpoint (JSON)"""
    return {
        "status": "healthy",
        "message": "NEXORA Search Engine is running",
        "version": "1.0.0",
        "indexed_documents": search_engine.num_docs if search_engine else 0,
        "cache_enabled": cache._client is not None,
    }


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query", min_length=1),
    top_k: int = Query(default=10, ge=1, le=100, description="Number of results")
):
    """
    Search documents using BM25 ranking algorithm
    
    **THIS IS THE FIXED VERSION** - Now uses actual BM25 instead of substring matching!
    
    Parameters:
    - q: Search query (required)
    - top_k: Number of top results to return (default: 10)
    
    Returns:
    - Ranked search results with BM25 scores
    """
    if not search_engine:
        return {
            "error": "Search engine not initialized",
            "query": q,
            "results": []
        }
    
    # Use the actual BM25 search engine (NOT substring matching!)
    result = await search_engine.search(q, top_k=top_k, use_cache=settings.use_cache)
    
    logger.info("search_completed",
                query=q,
                top_k=top_k,
                results_count=len(result["results"]),
                cached=result["cached"],
                search_time_ms=result["search_time_ms"])
    
    return result


@app.get("/documents")
async def list_documents():
    """List all indexed documents"""
    if not search_engine:
        return {"error": "Search engine not initialized"}
    
    docs = []
    for doc_id, content in search_engine.documents.items():
        docs.append({
            "doc_id": doc_id,
            "preview": content[:200] + "..." if len(content) > 200 else content,
            "length": len(content),
            "word_count": search_engine.doc_lengths.get(doc_id, 0)
        })
    
    return {
        "total_documents": len(docs),
        "documents": docs
    }


@app.get("/stats")
async def get_stats():
    """Get search engine statistics"""
    if not search_engine:
        return {"error": "Search engine not initialized"}
    
    return {
        "engine": {
            "indexed_documents": search_engine.num_docs,
            "average_doc_length": round(search_engine.avg_doc_len, 2),
            "total_unique_terms": len(search_engine.inverted_index),
            "algorithm": "BM25",
            "parameters": {
                "k1": settings.bm25_k1,
                "b": settings.bm25_b
            }
        },
        "cache": {
            "enabled": cache._client is not None,
            "ttl_seconds": settings.cache_ttl
        }
    }


@app.post("/cache/clear")
async def clear_cache():
    """Clear all cached search results"""
    count = await cache.invalidate("search:*")
    return {
        "status": "success",
        "message": f"Cleared {count} cached queries"
    }