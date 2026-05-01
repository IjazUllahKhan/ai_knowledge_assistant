from pydantic import BaseModel, Field
from typing import List, Optional


class YouTubeIngestRequest(BaseModel):
    url: str = Field(..., example="https://www.youtube.com/watch?v=q4YBbyyu9mk")
    chunk_size: int = Field(800, gt=100)
    chunk_overlap: int = Field(150, ge=0)


class IngestResponse(BaseModel):
    message: str
    source_type: str
    identifier: str
    chunks_added: int


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str = Field("default")
    top_k: int = Field(4, ge=1, le=20)


class SourceDocument(BaseModel):
    text: str
    source_type: str
    identifier: str
    chunk_index: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    session_id: str


class HealthResponse(BaseModel):
    status: str
    faiss_index_exists: bool
    total_documents: int
    sessions_active: int
