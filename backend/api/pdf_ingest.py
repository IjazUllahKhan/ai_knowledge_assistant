from fastapi import APIRouter, File, Form, UploadFile
from models.schemas import IngestResponse
from services.pdf import ingest_pdf
from services.vectorstore import add_documents

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/pdf", response_model=IngestResponse, summary="Ingest a PDF document")
async def ingest_pdf_endpoint(
    file:          UploadFile = File(...),
    chunk_size:    int        = Form(800),
    chunk_overlap: int        = Form(150),
):
    # HTTPException from the service layer bubbles up with its own status code
    file_name, docs = ingest_pdf(
        file=file,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    add_documents(docs)
    return IngestResponse(
        message="PDF ingested successfully.",
        source_type="pdf",
        identifier=file_name,
        chunks_added=len(docs),
    )
