import { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import styles from './ChatWindow.module.css';

const SUGGESTIONS = [
  'What are the main topics covered?',
  'Summarize the key points.',
  'What conclusions were drawn?',
  'Explain the most important concept.',
];

export default function ChatWindow({ messages, onSend, loading, hasContent }) {
  const inputRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function submit() {
    const text = inputRef.current?.value?.trim();
    if (!text || loading) return;
    onSend(text);
    inputRef.current.value = '';
  }

  return (
    <div className={styles.window}>
      {/* Messages area */}
      <div className={styles.messages}>
        {messages.length === 0 ? (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>🔍</div>
            <h2 className={styles.emptyTitle}>Ask your documents anything</h2>
            <p className={styles.emptySub}>
              Ingest a YouTube video or PDF using the sidebar, then start asking questions.
            </p>
            {hasContent && (
              <div className={styles.suggestions}>
                {SUGGESTIONS.map((s, i) => (
                  <button
                    key={i}
                    className={styles.suggestion}
                    onClick={() => onSend(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((m, i) => (
              <ChatMessage key={i} message={m} />
            ))}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className={styles.inputBar}>
        <div className={styles.inputWrap}>
          <textarea
            ref={inputRef}
            className={styles.textarea}
            placeholder="Ask a question about your documents… (Enter to send)"
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={loading}
          />
          <button
            className={styles.sendBtn}
            onClick={submit}
            disabled={loading}
            title="Send"
          >
            {loading ? <span className={styles.spinner} /> : <SendIcon />}
          </button>
        </div>
        <p className={styles.hint}>
          The agent automatically decides whether to query YouTube, PDF, or both sources.
        </p>
      </div>
    </div>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}
