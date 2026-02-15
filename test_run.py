from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create app
app = FastAPI(title="NEXORA Test Server")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "NEXORA running ✅",
        "message": "Server is working!",
        "endpoints": {
            "health": "http://localhost:8000/",
            "search": "http://localhost:8000/search?q=test",
            "docs": "http://localhost:8000/docs"
        }
    })

@app.get("/search")
async def search(q: str = "default", top_k: int = 10):
    """Search endpoint"""
    return JSONResponse({
        "query": q,
        "results": [
            {
                "doc_id": "1", 
                "content": f"Sample result for: {q}", 
                "score": 1.0, 
                "rank": 1
            }
        ],
        "total_results": 1,
        "search_time_ms": 1.2,
        "cached": False
    })

if __name__ == "__main__":
    print("=" * 50)
    print("  NEXORA Test Server Starting...")
    print("=" * 50)
    print("\n✅ Server will be available at:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/docs")
    print("   - http://localhost:8000/search?q=test")
    print("\n📝 Press CTRL+C to stop\n")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="127.0.0.1",  # Changed from 0.0.0.0
        port=8000, 
        log_level="info"
    )
