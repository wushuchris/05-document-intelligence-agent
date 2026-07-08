import re
from typing import List

from src.document_schema import DocumentChunk


def tokenize(text: str) -> List[str]:
    """Convert text into simple lowercase tokens."""
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def score_chunk(query: str, chunk: DocumentChunk) -> int:
    """Score a chunk by keyword overlap with the query."""
    query_terms = set(tokenize(query))
    chunk_terms = tokenize(chunk.text)

    if not query_terms or not chunk_terms:
        return 0

    return sum(1 for term in chunk_terms if term in query_terms)


def search_chunks(query: str, chunks: List[DocumentChunk], top_k: int = 5) -> List[DocumentChunk]:
    """Return the most relevant chunks for a query."""
    scored = []

    for chunk in chunks:
        score = score_chunk(query, chunk)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [chunk for _, chunk in scored[:top_k]]
