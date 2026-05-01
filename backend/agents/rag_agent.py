"""
LangGraph agent — classify → retrieve → generate.
Single FAISS retrieval per question. Docs passed directly to generator.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, StateGraph

from services.rag_pipeline import run_rag
from services.vectorstore import has_source_type, similarity_search


class AgentState(TypedDict):
    question:       str
    history:        List[Dict[str, str]]
    top_k:          int
    source_filter:  str
    identifier:     Optional[str]
    retrieved_docs: List[Document]
    answer:         str


_YT_KW  = {"video", "youtube", "transcript", "watch", "clip", "speaker", "lecture"}
_PDF_KW = {"pdf", "document", "paper", "file", "report", "page", "chapter", "written"}


# ── Node 1: classify ─────────────────────────────────────────

def classify_node(state: AgentState) -> AgentState:
    q          = state["question"].lower()
    wants_yt   = any(kw in q for kw in _YT_KW)
    wants_pdf  = any(kw in q for kw in _PDF_KW)
    yt_exists  = has_source_type("youtube")
    pdf_exists = has_source_type("pdf")

    if   wants_yt  and not wants_pdf and yt_exists:  sf = "youtube"
    elif wants_pdf and not wants_yt  and pdf_exists: sf = "pdf"
    elif yt_exists  and not pdf_exists:              sf = "youtube"
    elif pdf_exists and not yt_exists:               sf = "pdf"
    else:                                            sf = "all"

    print(f"[Agent] classify → {sf}  (yt={yt_exists} pdf={pdf_exists})")
    return {**state, "source_filter": sf, "identifier": None}


# ── Node 2: retrieve ─────────────────────────────────────────

def retrieve_node(state: AgentState) -> AgentState:
    sf   = state.get("source_filter", "all")
    docs = similarity_search(
        state["question"],
        k=state["top_k"],
        source_type=None if sf == "all" else sf,
        identifier=state.get("identifier"),
    )
    print(f"[Agent] retrieve → {len(docs)} docs (filter={sf})")
    for d in docs:
        print(f"  └─ {d.metadata.get('source_type')} | "
              f"{d.metadata.get('identifier')} | "
              f"chunk {d.metadata.get('chunk_index')}")
    return {**state, "retrieved_docs": docs}


# ── Node 3: generate ─────────────────────────────────────────

def generate_node(state: AgentState) -> AgentState:
    """Pass already-retrieved docs — no second FAISS call."""
    answer = run_rag(
        question=state["question"],
        history=state["history"],
        docs=state["retrieved_docs"],
    )
    return {**state, "answer": answer}


# ── Graph ─────────────────────────────────────────────────────

def _build() -> Any:
    g = StateGraph(AgentState)
    g.add_node("classify", classify_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)
    g.set_entry_point("classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()


_graph = _build()


# ── Public ────────────────────────────────────────────────────

def run_agent(
    question: str,
    history:  List[Dict[str, str]] | None = None,
    top_k:    int = 4,
) -> Dict[str, Any]:
    final = _graph.invoke({
        "question":       question,
        "history":        history or [],
        "top_k":          top_k,
        "source_filter":  "all",
        "identifier":     None,
        "retrieved_docs": [],
        "answer":         "",
    })
    return {
        "answer":         final["answer"],
        "retrieved_docs": final["retrieved_docs"],
        "source_filter":  final.get("source_filter", "all"),
    }
