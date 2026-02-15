"""Web crawler for document collection"""
import json
import os
from typing import Dict
import requests


def _sample_documents() -> Dict[str, str]:
    """Return minimal in-memory docs when crawl/cache is empty."""
    return {
        "1": "Python is a programming language. It is used for web development and data science.",
        "2": "Machine learning is a branch of artificial intelligence.",
        "3": "Data science uses statistics and programming to analyze data.",
    }
from bs4 import BeautifulSoup
from src.logger import logger
from src.config import settings

def crawl_web(urls: list, max_pages: int = 10, max_chars: int = 5000) -> Dict[str, str]:
    """
    Crawl web pages and extract text
    
    Args:
        urls: List of URLs to crawl
        max_pages: Maximum number of pages to crawl
        max_chars: Maximum characters per page
        
    Returns:
        Dictionary of {doc_id: text}
    """
    docs = {}
    doc_id = 1
    
    for url in urls[:max_pages]:
        try:
            logger.info("crawling", url=url)
            res = requests.get(
                url,
                timeout=settings.crawl_timeout,
                headers={"User-Agent": settings.user_agent},
            )
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=" ", strip=True)
                text = text[:max_chars]
                
                docs[str(doc_id)] = text
                doc_id += 1
                logger.info("crawled_success", url=url, doc_id=doc_id-1, length=len(text))
            else:
                logger.warning("crawl_failed", url=url, status=res.status_code)
                
        except Exception as e:
            logger.error("crawl_error", url=url, error=str(e))
    
    logger.info("crawl_completed", total_docs=len(docs))
    return docs


def load_documents() -> Dict[str, str]:
    """
    Load documents from cache or crawl web
    
    Returns:
        Dictionary of {doc_id: text}
    """
    cache_file = "documents.json"
    
    if os.path.exists(cache_file):
        logger.info("loading_cached_documents", file=cache_file)
        with open(cache_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
        if not documents:
            logger.warning("cached_documents_empty_using_sample")
            documents = _sample_documents()
        else:
            logger.info("loaded_cached_documents", count=len(documents))
        return documents
    
    # Crawl web
    urls = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Data_science",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Natural_language_processing",
    ]
    
    documents = crawl_web(
        urls,
        max_pages=settings.max_crawl_pages,
        max_chars=settings.max_page_size,
    )

    # If crawl returned nothing, use minimal sample so app still runs
    if not documents:
        logger.warning("crawl_empty_using_sample_documents")
        documents = _sample_documents()

    # Cache documents
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    logger.info("cached_documents", file=cache_file, count=len(documents))

    return documents