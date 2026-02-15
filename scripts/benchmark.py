"""Benchmark script to measure search performance"""
import asyncio
import statistics
import time
import os
import sys

# Allow running as: python scripts/benchmark.py (project root added to path)
_bench_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_bench_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
os.chdir(_project_root)

from src.indexing.crawler import load_documents
from src.search.cache import cache
from src.search.engine import SearchEngine

async def benchmark():
    # Initialize
    print("Initializing search engine...")
    await cache.connect()
    documents = load_documents()
    engine = SearchEngine(documents)
    
    # Test queries
    queries = [
        "python programming",
        "machine learning",
        "data science",
        "web development",
        "artificial intelligence",
    ]
    
    # Benchmark without cache
    print("\nBenchmarking WITHOUT cache...")
    latencies_no_cache = []
    for query in queries * 10:  # 50 total queries
        start = time.time()
        await engine.search(query, top_k=10, use_cache=False)
        latency = (time.time() - start) * 1000
        latencies_no_cache.append(latency)
    
    print(f"  Average: {statistics.mean(latencies_no_cache):.2f}ms")
    print(f"  P50: {statistics.median(latencies_no_cache):.2f}ms")
    print(f"  P95: {sorted(latencies_no_cache)[int(len(latencies_no_cache)*0.95)]:.2f}ms")
    print(f"  P99: {sorted(latencies_no_cache)[int(len(latencies_no_cache)*0.99)]:.2f}ms")
    
    # Benchmark with cache
    print("\nBenchmarking WITH cache...")
    latencies_with_cache = []
    for query in queries * 10:  # 50 total queries
        start = time.time()
        await engine.search(query, top_k=10, use_cache=True)
        latency = (time.time() - start) * 1000
        latencies_with_cache.append(latency)
    
    print(f"  Average: {statistics.mean(latencies_with_cache):.2f}ms")
    print(f"  P50: {statistics.median(latencies_with_cache):.2f}ms")
    print(f"  P95: {sorted(latencies_with_cache)[int(len(latencies_with_cache)*0.95)]:.2f}ms")
    print(f"  P99: {sorted(latencies_with_cache)[int(len(latencies_with_cache)*0.99)]:.2f}ms")
    
    # Calculate speedup
    speedup = statistics.mean(latencies_no_cache) / statistics.mean(latencies_with_cache)
    print(f"\nSpeedup: {speedup:.2f}x faster with cache")
    
    await cache.disconnect()

if __name__ == "__main__":
    asyncio.run(benchmark())