import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 120000,           // 2 min — LLM can be slow
});

// ── Ingestion ────────────────────────────────────────────────

export async function ingestYoutube(url, chunkSize = 800, chunkOverlap = 150) {
  const { data } = await api.post('/ingest/youtube', {
    url,
    chunk_size: chunkSize,
    chunk_overlap: chunkOverlap,
  });
  return data;
}

export async function ingestPdf(file, chunkSize = 800, chunkOverlap = 150) {
  const form = new FormData();
  form.append('file', file);
  form.append('chunk_size', chunkSize);
  form.append('chunk_overlap', chunkOverlap);
  const { data } = await api.post('/ingest/pdf', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

// ── Chat ─────────────────────────────────────────────────────

export async function sendChat(question, sessionId, topK = 4) {
  const { data } = await api.post('/chat', {
    question,
    session_id: sessionId,
    top_k: topK,
  });
  return data;
}

// ── Health ───────────────────────────────────────────────────

export async function fetchHealth() {
  const { data } = await api.get('/health');
  return data;
}
