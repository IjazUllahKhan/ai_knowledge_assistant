"""
/chat — session-aware Q&A via LangGraph agent.
Session memory is capped to prevent unbounded memory growth in production.
"""
from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse, SourceDocument
from agents.rag_agent import run_agent
from config import SESSION_MAX_TURNS

router = APIRouter(tags=["Chat"])

# {session_id: [{"role": "user"|"assistant", "content": "..."}]}
_sessions: Dict[str, List[dict]] = defaultdict(list)


def get_session_count() -> int:
    return len(_sessions)


def _trim_session(session: List[dict]) -> List[dict]:
    """Keep only the last N turns (2 messages per turn = user + assistant)."""
    max_messages = SESSION_MAX_TURNS * 2
    if len(session) > max_messages:
        return session[-max_messages:]
    return session


@router.post("/chat", response_model=ChatResponse, summary="Ask a question")
def chat(req: ChatRequest):
    history = _sessions[req.session_id]

    result  = run_agent(
        question=req.question,
        history=history,
        top_k=req.top_k,
    )

    answer = result["answer"]
    docs   = result["retrieved_docs"]

    # Append and trim
    history.append({"role": "user",      "content": req.question})
    history.append({"role": "assistant", "content": answer})
    _sessions[req.session_id] = _trim_session(history)

    sources = [
        SourceDocument(
            text=doc.page_content[:400],
            source_type=doc.metadata.get("source_type", "unknown"),
            identifier=doc.metadata.get("identifier", ""),
            chunk_index=doc.metadata.get("chunk_index"),
        )
        for doc in docs
    ]

    return ChatResponse(answer=answer, sources=sources, session_id=req.session_id)
