"""BM25 search engine for Nexora."""
import math
import time
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from src.config import settings
from src.indexing.tokenizer import normalize_query, tokenize
from src.search.cache import cache


class SearchEngine:
    """In-memory BM25 search over a doc id -> text mapping."""

    def __init__(self, documents: Dict[str, str]) -> None:
        self.documents = documents
        self.inverted_index: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_len = 0.0
        self.num_docs = len(documents)
        self._build_index()

    def _build_index(self) -> None:
        total_len = 0
        for doc_id, content in self.documents.items():
            tokens = tokenize(content)
            self.doc_lengths[doc_id] = len(tokens)
            total_len += len(tokens)
            for term, freq in Counter(tokens).items():
                self.inverted_index[term][doc_id] = freq
        self.avg_doc_len = total_len / self.num_docs if self.num_docs else 0.0

    def _bm25(self, term: str, doc_id: str, freq: int) -> float:
        df = len(self.inverted_index.get(term, {}))
        if df == 0 or self.num_docs == 0:
            return 0.0
        k1 = getattr(settings, "bm25_k1", 1.5)
        b = getattr(settings, "bm25_b", 0.75)
        idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
        doc_len = self.doc_lengths.get(doc_id, 0)
        denom = freq + k1 * (1 - b + b * doc_len / (self.avg_doc_len or 1.0))
        return idf * (freq * (k1 + 1)) / (denom or 1.0)

    def _score(self, terms: List[str]) -> List[Tuple[str, float]]:
        scores: Dict[str, float] = defaultdict(float)
        for term in terms:
            for doc_id, freq in self.inverted_index.get(term, {}).items():
                scores[doc_id] += self._bm25(term, doc_id, freq)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    async def search(
        self, query: str, top_k: int = 10, use_cache: bool = True
    ) -> Dict:
        t0 = time.time()
        normalized = normalize_query(query)
        max_r = getattr(settings, "max_results", 100)
        top_k = min(top_k, max_r)
        cache_key = f"search:{normalized}:{top_k}"

        if use_cache:
            cached = await cache.get(cache_key)
            if cached is not None:
                cached["cached"] = True
                return cached

        terms = tokenize(normalized)
        ranked = self._score(terms)
        results = []
        for rank, (doc_id, score) in enumerate(ranked[:top_k], start=1):
            content = self.documents.get(doc_id, "")
            results.append({
                "doc_id": doc_id,
                "content": content,
                "score": float(score),
                "rank": rank,
                "highlights": [content[:200]],
            })
        search_time_ms = (time.time() - t0) * 1000.0
        out = {
            "query": normalized,
            "results": results,
            "total_results": len(ranked),
            "search_time_ms": search_time_ms,
            "cached": False,
        }
        if use_cache and results:
            await cache.set(cache_key, out)
        return out
