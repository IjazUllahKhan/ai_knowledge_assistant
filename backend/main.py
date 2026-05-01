"""
FastAPI entry point — production ready.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS
from api.ingest import router as yt_router
from api.pdf_ingest import router as pdf_router
from api.chat import router as chat_router
from api.health import router as health_router

app = FastAPI(
    title="Multi-Source AI Knowledge Assistant",
    description="Agentic RAG — YouTube + PDF with LangGraph and Groq.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(yt_router)
app.include_router(pdf_router)
app.include_router(chat_router)
app.include_router(health_router)


@app.get("/", tags=["Root"])
def root():
    return {"status": "running", "docs": "/docs"}
