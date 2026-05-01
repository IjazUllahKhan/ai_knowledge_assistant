import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { sendChat, fetchHealth } from './api';
import './App.css';

// Stable session ID for this browser tab
const SESSION_ID = uuidv4();

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function App() {
  const [messages, setMessages]   = useState([]);
  const [loading, setLoading]     = useState(false);
  const [sources, setSources]     = useState([]);   // ingested sources list
  const [health, setHealth]       = useState(null);

  // Poll health every 15 s
  useEffect(() => {
    async function poll() {
      try { setHealth(await fetchHealth()); } catch {}
    }
    poll();
    const id = setInterval(poll, 15000);
    return () => clearInterval(id);
  }, []);

  function handleIngest(data) {
    setSources(prev => {
      // avoid duplicates
      const exists = prev.some(
        s => s.type === data.type && s.identifier === data.identifier
      );
      return exists ? prev : [...prev, data];
    });
    // refresh health immediately
    fetchHealth().then(setHealth).catch(() => {});
  }

  const handleSend = useCallback(async (question) => {
    if (loading) return;

    // Append user message
    setMessages(prev => [
      ...prev,
      { role: 'user', content: question, timestamp: now() },
      { role: 'assistant', typing: true },   // placeholder
    ]);
    setLoading(true);

    try {
      const data = await sendChat(question, SESSION_ID, 4);
      setMessages(prev => [
        ...prev.slice(0, -1),   // remove typing placeholder
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          timestamp: now(),
        },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Server error';
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: `⚠️ Error: ${detail}`,
          timestamp: now(),
        },
      ]);
    }
    setLoading(false);
  }, [loading]);

  const hasContent = health?.faiss_index_exists || sources.length > 0;

  return (
    <div className="app">
      <Sidebar onIngest={handleIngest} sources={sources} health={health} />
      <ChatWindow
        messages={messages}
        onSend={handleSend}
        loading={loading}
        hasContent={hasContent}
      />
    </div>
  );
}
