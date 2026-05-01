import { useState } from 'react';
import { ingestYoutube, ingestPdf } from '../api';
import styles from './Sidebar.module.css';

// ── Small status badge ───────────────────────────────────────
function StatusBadge({ status }) {
  if (!status) return null;
  const isError = status.type === 'error';
  return (
    <div className={`${styles.badge} ${isError ? styles.badgeError : styles.badgeSuccess}`}>
      <span className={styles.badgeDot} />
      <span>{status.message}</span>
    </div>
  );
}

// ── YouTube panel ────────────────────────────────────────────
function YoutubePanel({ onIngest }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  async function handle() {
    if (!url.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      const data = await ingestYoutube(url.trim());
      setStatus({ type: 'success', message: `✓ ${data.chunks_added} chunks · ${data.identifier}` });
      onIngest({ type: 'youtube', ...data });
      setUrl('');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Ingestion failed';
      setStatus({ type: 'error', message: `✗ ${msg}` });
    }
    setLoading(false);
  }

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <span className={styles.panelIcon} style={{ background: 'var(--red-dim)', color: 'var(--red)' }}>▶</span>
        <span className={styles.panelTitle}>YouTube Video</span>
      </div>
      <input
        className={styles.input}
        value={url}
        onChange={e => setUrl(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handle()}
        placeholder="https://youtube.com/watch?v=..."
        disabled={loading}
      />
      <button
        className={`${styles.btn} ${styles.btnRed}`}
        onClick={handle}
        disabled={loading || !url.trim()}
      >
        {loading ? <span className={styles.spinner} /> : null}
        {loading ? 'Processing…' : 'Ingest Video'}
      </button>
      <StatusBadge status={status} />
    </div>
  );
}

// ── PDF panel ────────────────────────────────────────────────
function PdfPanel({ onIngest }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  async function handle() {
    if (!file) return;
    setLoading(true);
    setStatus(null);
    try {
      const data = await ingestPdf(file);
      setStatus({ type: 'success', message: `✓ ${data.chunks_added} chunks · ${data.identifier}` });
      onIngest({ type: 'pdf', ...data });
      setFile(null);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Ingestion failed';
      setStatus({ type: 'error', message: `✗ ${msg}` });
    }
    setLoading(false);
  }

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <span className={styles.panelIcon} style={{ background: 'var(--blue-dim)', color: 'var(--blue)' }}>📄</span>
        <span className={styles.panelTitle}>PDF Document</span>
      </div>
      <label className={styles.fileLabel}>
        <input
          type="file"
          accept=".pdf"
          className={styles.fileInput}
          onChange={e => setFile(e.target.files[0] || null)}
          disabled={loading}
        />
        <span className={styles.fileLabelText}>
          {file ? file.name : 'Click to choose a PDF…'}
        </span>
      </label>
      <button
        className={`${styles.btn} ${styles.btnBlue}`}
        onClick={handle}
        disabled={loading || !file}
      >
        {loading ? <span className={styles.spinner} /> : null}
        {loading ? 'Processing…' : 'Ingest PDF'}
      </button>
      <StatusBadge status={status} />
    </div>
  );
}

// ── Ingested sources list ────────────────────────────────────
function SourcesList({ sources }) {
  if (!sources.length) return null;
  return (
    <div className={styles.sourcesList}>
      <div className={styles.sourcesTitle}>Ingested Sources</div>
      {sources.map((s, i) => (
        <div key={i} className={styles.sourceItem}>
          <span className={s.type === 'youtube' ? styles.tagYt : styles.tagPdf}>
            {s.type === 'youtube' ? '▶' : '📄'}
          </span>
          <span className={styles.sourceId}>{s.identifier}</span>
          <span className={styles.sourceChunks}>{s.chunks_added}c</span>
        </div>
      ))}
    </div>
  );
}

// ── Main sidebar ─────────────────────────────────────────────
export default function Sidebar({ onIngest, sources, health }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>🧠</span>
        <div>
          <div className={styles.logoTitle}>Knowledge Assistant</div>
          <div className={styles.logoSub}>Multi-Source Agentic RAG</div>
        </div>
      </div>

      {health && (
        <div className={styles.healthBar}>
          <span className={`${styles.healthDot} ${health.faiss_index_exists ? styles.dotGreen : styles.dotYellow}`} />
          <span>
            {health.faiss_index_exists
              ? `${health.total_documents} vectors · ${health.sessions_active} sessions`
              : 'No index yet — ingest a source'}
          </span>
        </div>
      )}

      <YoutubePanel onIngest={onIngest} />
      <PdfPanel onIngest={onIngest} />
      <SourcesList sources={sources} />
    </aside>
  );
}
