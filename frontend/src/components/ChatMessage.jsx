import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import SourceCard from './SourceCard';
import styles from './ChatMessage.module.css';

function TypingDots() {
  return (
    <div className={styles.typingDots}>
      <span /><span /><span />
    </div>
  );
}

export default function ChatMessage({ message }) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === 'user';
  const hasSources = message.sources && message.sources.length > 0;

  if (message.typing) {
    return (
      <div className={`${styles.row} ${styles.rowAssistant}`}>
        <div className={styles.avatarAssistant}>🧠</div>
        <div className={`${styles.bubble} ${styles.bubbleAssistant}`}>
          <TypingDots />
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.row} ${isUser ? styles.rowUser : styles.rowAssistant}`}>
      {!isUser && <div className={styles.avatarAssistant}>🧠</div>}

      <div className={styles.content}>
        <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAssistant}`}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                code({ inline, children }) {
                  return inline
                    ? <code className={styles.inlineCode}>{children}</code>
                    : <pre className={styles.codeBlock}><code>{children}</code></pre>;
                },
                p({ children }) { return <p className={styles.para}>{children}</p>; },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {hasSources && (
          <div className={styles.sourcesSection}>
            <button
              className={styles.sourcesToggle}
              onClick={() => setShowSources(v => !v)}
            >
              <span>{showSources ? '▾' : '▸'}</span>
              {message.sources.length} source{message.sources.length !== 1 ? 's' : ''} retrieved
            </button>
            {showSources && (
              <div className={styles.sourcesList}>
                {message.sources.map((s, i) => (
                  <SourceCard key={i} source={s} index={i} />
                ))}
              </div>
            )}
          </div>
        )}

        {message.timestamp && (
          <div className={`${styles.ts} ${isUser ? styles.tsRight : styles.tsLeft}`}>
            {message.timestamp}
          </div>
        )}
      </div>

      {isUser && <div className={styles.avatarUser}>👤</div>}
    </div>
  );
}
