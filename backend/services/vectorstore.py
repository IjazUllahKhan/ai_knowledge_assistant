"""
FAISS vector store — in-memory only, never persisted to disk.
Fresh on every server start — no stale data between sessions.
"""
import threading
from typing import Dict, List, Optional, Set

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from services.embeddings import get_embeddings

_lock:     threading.Lock       = threading.Lock()
_store:    Optional[FAISS]      = None
_ingested: Dict[str, Set[str]]  = {"youtube": set(), "pdf": set()}


def add_documents(docs: List[Document]) -> None:
    global _store
    embeddings = get_embeddings()
    with _lock:
        if _store is None:
            _store = FAISS.from_documents(docs, embeddings)
        else:
            _store.add_documents(docs)
        for doc in docs:
            src  = doc.metadata.get("source_type", "")
            iden = doc.metadata.get("identifier", "")
            if src in _ingested and iden:
                _ingested[src].add(iden)
    print(f"[Store] +{len(docs)} docs | {get_ingested_sources()}")


def similarity_search(
    query: str,
    k: int = 4,
    source_type: Optional[str] = None,
    identifier: Optional[str] = None,
) -> List[Document]:
    if _store is None:
        return []

    total = document_count()
    if total == 0:
        return []

    # Over-fetch to allow for post-filter, but never exceed what's in store
    fetch_k = min(k * 8, total) if (source_type or identifier) else min(k, total)

    results = _store.similarity_search(query, k=fetch_k)

    if source_type:
        results = [d for d in results if d.metadata.get("source_type") == source_type]
    if identifier:
        results = [d for d in results if d.metadata.get("identifier") == identifier]

    return results[:k]


def clear_store() -> None:
    global _store, _ingested
    with _lock:
        _store    = None
        _ingested = {"youtube": set(), "pdf": set()}
    print("[Store] cleared.")


def get_ingested_sources() -> Dict[str, List[str]]:
    return {k: list(v) for k, v in _ingested.items()}


def has_source_type(source_type: str) -> bool:
    return bool(_ingested.get(source_type))


def document_count() -> int:
    if _store is None:
        return 0
    try:
        return _store.index.ntotal
    except Exception:
        return 0
