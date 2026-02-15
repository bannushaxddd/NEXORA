"""Benchmark script to measure search performance"""
import time
import asyncio
import statistics
from src.search.engine import SearchEngine
from src.search.cache import cache
from src.indexing.crawler import load_documents

async def benchmark():
    # Initialize
    print("🚀 Initializing search engine...")
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
    print("\n📊 Benchmarking WITHOUT cache...")
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
    print("\n📊 Benchmarking WITH cache...")
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
    print(f"\n🚀 Speedup: {speedup:.2f}x faster with cache")
    
    await cache.disconnect()

if __name__ == "__main__":
    asyncio.run(benchmark())