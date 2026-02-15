"""Text tokenization and preprocessing"""
import re
from typing import List

def tokenize(text: str) -> List[str]:
    """
    Tokenize text into lowercase words
    
    Args:
        text: Input text
        
    Returns:
        List of tokens
    """
    # Convert to lowercase and extract words
    tokens = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Remove stopwords (simple version)
    stopwords = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with'
    }
    tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
    
    return tokens


def normalize_query(query: str) -> str:
    """
    Normalize query text
    
    Args:
        query: Input query
        
    Returns:
        Normalized query
    """
    # Convert to lowercase
    query = query.lower().strip()
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query)
    
    return query