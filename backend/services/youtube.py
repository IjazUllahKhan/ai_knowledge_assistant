"""
YouTube ingestion service.
"""
import re
from typing import List

from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi


def _extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.match(r"^[0-9A-Za-z_-]{11}$", url.strip()):
        return url.strip()
    raise HTTPException(
        status_code=422,
        detail=f"Could not extract a valid YouTube video ID from: {url}",
    )


def _fetch_transcript(video_id: str) -> str:
    """
    Fetch transcript using the installed youtube-transcript-api API.
    """
    api = YouTubeTranscriptApi()
    try:
        data = api.fetch(video_id, languages=["en"])
    except Exception as exc:
        try:
            transcript_list = api.list(video_id)
            transcript = next(iter(transcript_list))
            data = transcript.fetch()
        except Exception as exc2:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript unavailable for video '{video_id}': {exc2}",
            )

    chunks: list[str] = []
    for item in data:
        if hasattr(item, "text"):
            chunks.append(item.text)
        elif isinstance(item, dict):
            chunks.append(item.get("text", ""))
    return " ".join(chunks)


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.encode("ascii", errors="ignore").decode()
    return text.strip()


def ingest_youtube(
    url: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> tuple[str, List[Document]]:
    video_id = _extract_video_id(url)
    raw_text = _fetch_transcript(video_id)
    clean    = _clean_text(raw_text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    raw_docs = splitter.create_documents([clean])

    docs: List[Document] = [
        Document(
            page_content=doc.page_content,
            metadata={
                "source_type": "youtube",
                "video_id":    video_id,
                "chunk_index": i,
                "identifier":  video_id,
            },
        )
        for i, doc in enumerate(raw_docs)
    ]
    return video_id, docs
