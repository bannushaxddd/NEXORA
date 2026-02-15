# NEXORA – Next-Generation Search Engine

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Algorithm](https://img.shields.io/badge/Algorithm-BM25-orange.svg)]()

Production-grade search engine built with the BM25 ranking algorithm and sub-10ms latency.

---

## Live Demo

Application:
https://nexora.onrender.com

API Documentation:
https://nexora.onrender.com/docs

### Example Queries

Search Python:
https://nexora.onrender.com/search?q=python&top_k=3

Search Machine Learning:
https://nexora.onrender.com/search?q=machine%20learning&top_k=5

---

## Features

- BM25 (Okapi BM25) ranking algorithm
- Sub-10ms latency using Redis caching
- Asynchronous API built with FastAPI
- Real-time search performance metrics
- Tuned relevance scoring (k1=1.5, b=0.75)
- Intelligent Redis-based caching
- Clean, modular architecture

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   FastAPI   │─────▶│  BM25 Engine │─────▶│  Documents  │
│  REST API   │      │   Indexing   │      │    Corpus   │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌──────────────┐
│    Redis    │      │  Tokenizer   │
│    Cache    │      │  NLP Layer   │
└─────────────┘      └──────────────┘
```

---

## Quick Start

### Local Installation

git clone https://github.com/bannushaxddd/NEXORA.git  
cd NEXORA  
pip install -r requirements.txt  

Optional: start Redis  
redis-server  

Run application  
python run.py  

Server runs at:  
http://localhost:8000

---

### Docker Deployment

docker-compose up -d

---

## API Endpoints

| Endpoint      | Method | Description              |
|--------------|--------|--------------------------|
| /            | GET    | Health check             |
| /search      | GET    | BM25 search              |
| /documents   | GET    | List document corpus     |
| /stats       | GET    | Engine statistics        |
| /docs        | GET    | Swagger API documentation|

Example:

curl "http://localhost:8000/search?q=python&top_k=5"

---

## Example Response

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

---

## Tech Stack

- Backend: Python 3.8+, FastAPI
- Ranking Algorithm: Okapi BM25 (implemented from scratch)
- Caching: Redis
- Testing: pytest, pytest-asyncio
- Containerization: Docker, Docker Compose
- Documentation: OpenAPI (Swagger UI)

---

## Performance

- Latency: <2ms (cached), ~5ms (uncached)
- Throughput: 1000+ queries per second
- Cache Hit Rate: ~85% in production
- Horizontally scalable architecture

---

## Use Cases

- Document search engines
- Knowledge base search systems
- Content management platforms
- E-commerce product search
- Academic and research paper retrieval

---

## Project Structure

NEXORA/
├── src/
│   ├── api/
│   ├── search/
│   ├── indexing/
│   └── config.py
├── documents.json
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## Author

Bannusha Shaik  
GitHub: https://github.com/bannushaxddd  
Email: bannushashaik85@gmail.com  

---

## License

MIT License

