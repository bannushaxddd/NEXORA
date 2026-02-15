#!/usr/bin/env python3
"""
Run NEXORA Search Engine
"""
import uvicorn

if __name__ == "__main__":
    print("\n🚀 Starting NEXORA Search Engine...\n")
    
    uvicorn.run(
        "src.api.routes:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )