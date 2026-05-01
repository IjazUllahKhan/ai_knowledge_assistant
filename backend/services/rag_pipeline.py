"""
RAG pipeline — retrieval + Groq generation.
Reads config once at import time — no per-request file I/O.
"""
import requests
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from config import GROQ_API_KEY, GROQ_MODEL, LLM_MAX_TOKENS
from services.vectorstore import similarity_search

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_HEADERS   = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type":  "application/json",
}

# ── Prompt ────────────────────────────────────────────────────

_PROMPT = PromptTemplate(
    template="""You are a helpful AI assistant answering questions from documents.
Use ONLY the context below to answer. If the answer is not in the context, say:
"I don't have enough information to answer that."
Be concise and mention whether the source is YouTube or PDF.

Context:
{context}

Chat History:
{history}

Question: {question}

Answer:""",
    input_variables=["context", "history", "question"],
)


# ── Groq call ─────────────────────────────────────────────────

def call_llm(prompt: str) -> str:
    # Hard cap — Groq context window limit
    if len(prompt) > 6000:
        prompt = prompt[:6000] + "\n...[context truncated]\n\nAnswer:"

    payload = {
        "model":       GROQ_MODEL,
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  LLM_MAX_TOKENS,
        "temperature": 0.3,
    }

    try:
        r = requests.post(_GROQ_URL, headers=_HEADERS, json=payload, timeout=60)
        print(f"[Groq] status={r.status_code} model={GROQ_MODEL}")

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()

        if r.status_code == 401:
            return "Invalid Groq API key. Check GROQ_API_KEY in .env"

        if r.status_code == 429:
            return "Groq rate limit reached. Wait a moment and retry."

        if r.status_code == 400:
            detail = r.json().get("error", {}).get("message", r.text[:200])
            # Retry once with a shorter prompt
            short_payload = {
                **payload,
                "messages": [{"role": "user", "content": prompt[:3000] + "\n\nAnswer briefly:"}],
            }
            retry = requests.post(_GROQ_URL, headers=_HEADERS, json=short_payload, timeout=60)
            if retry.status_code == 200:
                return retry.json()["choices"][0]["message"]["content"].strip()
            return f"Groq error: {detail}"

        if r.status_code == 404:
            return f"Groq model '{GROQ_MODEL}' not found. Update GROQ_MODEL in .env"

        return f"Groq error {r.status_code}: {r.text[:200]}"

    except requests.exceptions.Timeout:
        return "Groq timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Cannot reach Groq API. Check your internet connection."
    except Exception as e:
        print(f"[Groq] Unexpected error: {e}")
        return f"Unexpected error: {e}"


# ── Helpers ───────────────────────────────────────────────────

def _build_context(docs: List[Document]) -> str:
    parts = []
    for doc in docs:
        src   = doc.metadata.get("source_type", "unknown")
        ident = doc.metadata.get("identifier", "")
        label = f"[YouTube: {ident}]" if src == "youtube" else f"[PDF: {ident}]"
        parts.append(f"{label}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _format_history(messages: list) -> str:
    if not messages:
        return "None"
    return "\n".join(
        f"{m.get('role', '').capitalize()}: {m.get('content', '')}"
        for m in messages[-6:]   # last 3 turns only
    )


# ── Main ─────────────────────────────────────────────────────

def run_rag(
    question: str,
    history: list,
    docs: List[Document],           # pre-retrieved — no double FAISS call
) -> str:
    """
    Build prompt from already-retrieved docs and call Groq.
    Docs are passed in from the agent — no second retrieval.
    """
    if not docs:
        return "No documents found. Please ingest a YouTube video or PDF first."

    rendered    = _PROMPT.invoke({
        "context":  _build_context(docs),
        "history":  _format_history(history),
        "question": question,
    })
    prompt_text = rendered.text if hasattr(rendered, "text") else str(rendered)
    print(f"[RAG] docs={len(docs)} prompt_len={len(prompt_text)}")

    answer = call_llm(prompt_text)

    # Strip prompt echo from some models
    if "Answer:" in answer:
        answer = answer.split("Answer:")[-1].strip()

    return answer
