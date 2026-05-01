"""
/health  — system status
/clear   — wipe in-memory store
/sources — list ingested sources this session
"""
from fastapi import APIRouter
from models.schemas import HealthResponse
from services.vectorstore import document_count, clear_store, get_ingested_sources
from api.chat import get_session_count

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="System health check")
def health():
    count = document_count()
    return HealthResponse(
        status="ok",
        faiss_index_exists=count > 0,
        total_documents=count,
        sessions_active=get_session_count(),
    )


@router.delete("/clear", summary="Wipe in-memory store and start fresh")
def clear():
    clear_store()
    return {"message": "Store cleared. Re-ingest your sources."}


@router.get("/sources", summary="List ingested sources this session")
def sources():
    return get_ingested_sources()
