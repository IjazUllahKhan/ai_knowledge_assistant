import styles from './SourceCard.module.css';

export default function SourceCard({ source, index }) {
  const isYt = source.source_type === 'youtube';
  return (
    <div className={`${styles.card} ${isYt ? styles.cardYt : styles.cardPdf}`}>
      <div className={styles.header}>
        <span className={isYt ? styles.tagYt : styles.tagPdf}>
          {isYt ? '▶ YouTube' : '📄 PDF'}
        </span>
        <span className={styles.ident}>{source.identifier}</span>
        {source.chunk_index != null && (
          <span className={styles.chunk}>chunk {source.chunk_index}</span>
        )}
      </div>
      <p className={styles.excerpt}>
        {source.text.length > 200 ? source.text.slice(0, 200) + '…' : source.text}
      </p>
    </div>
  );
}
