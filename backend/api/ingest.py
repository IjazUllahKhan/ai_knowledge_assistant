from fastapi import APIRouter, HTTPException
from models.schemas import YouTubeIngestRequest, IngestResponse
from services.youtube import ingest_youtube
from services.vectorstore import add_documents

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/youtube", response_model=IngestResponse, summary="Ingest a YouTube video")
def ingest_youtube_endpoint(req: YouTubeIngestRequest):
    # HTTPException from the service layer bubbles up with its own status code
    video_id, docs = ingest_youtube(
        url=req.url,
        chunk_size=req.chunk_size,
        chunk_overlap=req.chunk_overlap,
    )
    add_documents(docs)
    return IngestResponse(
        message="YouTube video ingested successfully.",
        source_type="youtube",
        identifier=video_id,
        chunks_added=len(docs),
    )
