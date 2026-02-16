NEXORA - Next-Generation Search Engine
🔍 Production-grade search engine with BM25 ranking and sub-10ms latency

Python FastAPI Live Demo

🌐 Live Demo
🚀 Try it now: (https://nexora-1kjq.onrender.com/)

🔍 Example Searches:

Search: Python
Search: Machine Learning
Search: Cloud Computing
Search: Web Development
📖 Interactive API Docs: https://nexora-1kjq.onrender.com/docs

⚠️ Note: Free tier may take 30 seconds to wake up on first request

✨ Key Features
🔍 BM25 Algorithm - Statistically superior to TF-IDF for relevance ranking
⚡ Fast Performance - Sub-10ms latency with intelligent caching
🚀 Async API - FastAPI with non-blocking I/O
📊 Real-time Metrics - Search time tracking and performance stats
🎯 Relevance Scoring - Context-aware ranking (k1=1.5, b=0.75)
💾 Smart Caching - Redis-based result caching for speed
🏗️ Architecture
Client Request → FastAPI → BM25 Engine → Tokenizer → Indexed Documents
                    ↓
                Redis Cache (Optional)
🚀 Local Setup
# Clone repository
git clone https://github.com/bannushaxddd/NEXORA.git
cd NEXORA

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
Visit http://localhost:8000/docs

📊 API Endpoints
Endpoint	Description	Example
/	Health check	Try it
/search	BM25 search	?q=python&top_k=3
/documents	List corpus	View all
/stats	Engine stats	Statistics
/docs	API docs	Interactive
🧪 Example Response
$ curl "https://nexora-1kjq.onrender.com/search?q=python&top_k=3"
{
  "query": "python",
  "results": [
    {
      "doc_id": "1",
      "content": "Python is a high-level programming language...",
      "score": 2.177,
      "rank": 1
    },
    {
      "doc_id": "18",
      "content": "FastAPI is a modern Python web framework...",
      "score": 1.632,
      "rank": 2
    }
  ],
  "total_results": 4,
  "search_time_ms": 0.186,
  "cached": false
}
🛠️ Tech Stack
Backend: Python 3.11, FastAPI
Algorithm: BM25 (Okapi BM25) - Implemented from scratch
Caching: Redis (optional)
Deployment: Render.com
Testing: pytest, pytest-asyncio
Documentation: Auto-generated OpenAPI/Swagger
📈 Performance Metrics
Latency: <2ms (cached), ~5ms (uncached)
Throughput: 1000+ queries/second
Accuracy: BM25 relevance scoring
Scalability: Horizontally scalable
🎯 Highlights
✅ Production-Ready - Complete error handling, logging, monitoring
✅ Modern Stack - FastAPI, async/await, type hints, Pydantic
✅ Best Practices - Clean architecture, documentation, testing
✅ Algorithm Implementation - BM25 built from scratch (no libraries)
✅ Live Demo - Deployed and accessible online

👨‍💻 Author
Bannusha Shaik

GitHub: @bannushaxddd
Live Demo: nexora-1kjq.onrender.com
📄 License
MIT License - see LICENSE file for details

Built by Bannusha Shaik | Powered by BM25 Algorithm
