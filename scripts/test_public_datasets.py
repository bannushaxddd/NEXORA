"""Test script for public datasets collection"""
import sys
import os
from pathlib import Path
from collections import Counter

# Fix Windows encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.indexing.public_datasets import (
    collect_public_datasets,
    fetch_hackernews_posts,
    fetch_reddit_posts,
    fetch_arxiv_abstracts,
    fetch_github_readmes,
)
from src.logger import logger, setup_logging

if __name__ == "__main__":
    setup_logging()
    
    print("=" * 60)
    print("Testing Public Datasets Collection")
    print("Target: 500-1000 documents")
    print("=" * 60)
    
    # Collect from each source individually to show breakdown
    print("\nCollecting documents from each source...\n")
    
    hn_docs = fetch_hackernews_posts(limit=250)
    print(f"[OK] HackerNews: {len(hn_docs)} documents")
    
    reddit_docs = fetch_reddit_posts(
        subreddits=["programming", "Python", "MachineLearning", "webdev", "compsci", 
                   "learnprogramming", "javascript", "rust", "golang", "cpp"],
        limit_per_sub=75
    )
    print(f"[OK] Reddit: {len(reddit_docs)} documents")
    
    arxiv_docs = fetch_arxiv_abstracts(
        categories=["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.SE", "cs.PL", "cs.NE", "cs.DS"],
        max_results=250
    )
    print(f"[OK] ArXiv: {len(arxiv_docs)} documents")
    
    github_docs = fetch_github_readmes(limit=150)
    print(f"[OK] GitHub: {len(github_docs)} documents")
    
    # Combine all documents
    all_docs = {}
    all_docs.update(hn_docs)
    all_docs.update(reddit_docs)
    all_docs.update(arxiv_docs)
    all_docs.update(github_docs)
    
    print("\n" + "=" * 60)
    print(f"TOTAL DOCUMENTS COLLECTED: {len(all_docs)}")
    print("=" * 60)
    
    # Check if we're in the target range
    if 500 <= len(all_docs) <= 1000:
        print(f"[SUCCESS] Collected {len(all_docs)} documents (within target range 500-1000)")
    elif len(all_docs) > 1000:
        print(f"[SUCCESS] Collected {len(all_docs)} documents (exceeds minimum of 500)")
    else:
        print(f"[WARNING] Only collected {len(all_docs)} documents (target: 500-1000)")
    
    # Show breakdown by source
    source_counts = Counter()
    for doc_id in all_docs.keys():
        if doc_id.startswith("hn_"):
            source_counts["HackerNews"] += 1
        elif doc_id.startswith("reddit_"):
            source_counts["Reddit"] += 1
        elif doc_id.startswith("arxiv_"):
            source_counts["ArXiv"] += 1
        elif doc_id.startswith("github_"):
            source_counts["GitHub"] += 1
    
    print("\nBreakdown by source:")
    for source, count in source_counts.most_common():
        print(f"  - {source}: {count} documents")
    
    # Show sample documents
    print(f"\nSample documents (first 5):")
    sample_ids = list(all_docs.keys())[:5]
    for i, doc_id in enumerate(sample_ids, 1):
        preview = all_docs[doc_id][:150].replace("\n", " ")
        print(f"\n  {i}. {doc_id}")
        print(f"     {preview}...")
    
    # Save to documents.json
    import json
    with open("documents.json", "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVED] documents.json with {len(all_docs)} documents")
    
    print("\n" + "=" * 60)
