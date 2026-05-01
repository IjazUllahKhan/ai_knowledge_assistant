"""
PDF ingestion service.
Reads PDF bytes directly in memory — nothing is saved to disk.
"""
import re
from typing import List

from fastapi import HTTPException, UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF


def _extract_text_from_upload(file: UploadFile) -> tuple[str, str]:
    """
    Read uploaded PDF bytes directly into PyMuPDF — no disk storage at all.
    Returns (file_name, raw_text).
    """
    file_name = file.filename or "upload.pdf"
    content   = file.file.read()
    try:
        doc        = fitz.open(stream=content, filetype="pdf")
        pages_text = [page.get_text() for page in doc]
        doc.close()
        return file_name, "\n".join(pages_text)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not read PDF '{file_name}': {exc}",
        )


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.encode("ascii", errors="ignore").decode()
    return text.strip()


def ingest_pdf(
    file: UploadFile,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> tuple[str, List[Document]]:
    """
    Full pipeline: UploadFile → extract text in memory → chunk → Documents.
    PDF bytes are never written to disk.
    Returns (file_name, list_of_documents).
    """
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported.")

    file_name, raw_text = _extract_text_from_upload(file)
    clean = _clean_text(raw_text)

    if not clean:
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the PDF.",
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    raw_docs = splitter.create_documents([clean])

    docs: List[Document] = [
        Document(
            page_content=doc.page_content,
            metadata={
                "source_type": "pdf",
                "file_name":   file_name,
                "chunk_index": i,
                "identifier":  file_name,
            },
        )
        for i, doc in enumerate(raw_docs)
    ]
    return file_name, docs
