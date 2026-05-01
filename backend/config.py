import os
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_env_path, override=True)

# ── HuggingFace — embeddings only ────────────────────────────
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN missing. Add it to backend/.env")

EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ── Groq — LLM ───────────────────────────────────────────────
GROQ_API_KEY: str   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str     = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "512"))

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing. Add it to backend/.env")

# ── Chunking ─────────────────────────────────────────────────
CHUNK_SIZE: int    = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

# ── RAG ──────────────────────────────────────────────────────
DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "4"))

# ── CORS — comma-separated, supports multiple deploy origins ─
ALLOWED_ORIGINS: list = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]

# ── Session memory cap (prevents memory leak in production) ──
SESSION_MAX_TURNS: int = int(os.getenv("SESSION_MAX_TURNS", "20"))

print(f"[config] model={GROQ_MODEL} | origins={ALLOWED_ORIGINS}")
