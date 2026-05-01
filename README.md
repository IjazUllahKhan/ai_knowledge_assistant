# 🧠 Multi-Source AI Knowledge Assistant

> An agentic RAG (Retrieval-Augmented Generation) system that lets you chat with **YouTube videos** and **PDF documents** using natural language.

Built with **FastAPI · LangGraph · FAISS · HuggingFace · Groq (LLaMA 3)**

---

## 📸 Demo

| Ingest a YouTube video | Ask questions | Upload a PDF |
|---|---|---|
| Paste any YouTube URL | Get answers grounded in the video | Upload any PDF and query it |

---

## ✨ Features

- 🎥 **YouTube ingestion** — paste any YouTube URL, transcript is extracted and indexed automatically
- 📄 **PDF ingestion** — upload any PDF, text extracted in-memory (no disk storage)
- 🤖 **LangGraph agent** — intelligently decides whether to search YouTube, PDF, or both
- 🔍 **FAISS vector search** — semantic similarity search, not keyword matching
- 🧠 **Session memory** — remembers last 20 turns of your conversation
- ⚡ **Groq LLM** — LLaMA 3.1 8B running at 800 tokens/second (free tier)
- 🌐 **React frontend** — clean dark-mode chat UI

---

## 🏗️ Architecture

```
User Question
      │
      ▼
LangGraph Agent
  ├── classify_node   → decides: youtube / pdf / all
  ├── retrieve_node   → FAISS semantic search (single call)
  └── generate_node   → Groq LLaMA 3.1 → grounded answer
      │
      ▼
Structured Response (answer + source chunks)
```

---

## 🗂️ Project Structure

```
ai_knowledge_assistant/
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # All settings from .env
│   ├── api/
│   │   ├── ingest.py            # POST /ingest/youtube
│   │   ├── pdf_ingest.py        # POST /ingest/pdf
│   │   ├── chat.py              # POST /chat
│   │   └── health.py            # GET /health, /sources, DELETE /clear
│   ├── services/
│   │   ├── youtube.py           # URL → transcript → chunks
│   │   ├── pdf.py               # PDF bytes → text → chunks (no disk write)
│   │   ├── embeddings.py        # HuggingFace sentence-transformers
│   │   ├── vectorstore.py       # In-memory FAISS store
│   │   └── rag_pipeline.py      # Prompt builder + Groq call
│   ├── agents/
│   │   └── rag_agent.py         # LangGraph graph
│   └── models/
│       └── schemas.py           # Pydantic models
├── frontend/                    # React chat UI
├── requirements.txt
└── README.md
```

---

## ⚡ Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Free [HuggingFace](https://huggingface.co/settings/tokens) token
- Free [Groq](https://console.groq.com) API key

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai_knowledge_assistant.git
cd ai_knowledge_assistant
```

### 2. Configure environment
```bash
cd backend
cp .env.example .env
```

Open `backend/.env` and fill in your keys:
```env
HF_TOKEN=hf_your_token_here
GROQ_API_KEY=gsk_your_key_here
```

### 3. Install Python dependencies
```bash
pip install -r ../requirements.txt
```

### 4. Start the backend
```bash
uvicorn main:app --reload
```
Backend runs at → http://localhost:8000
Swagger docs at → http://localhost:8000/docs

### 5. Start the frontend (new terminal)
```bash
cd frontend
npm install
npm start
```
Frontend runs at → http://localhost:3000

---

## 🔑 Environment Variables

| Variable | Required | Description | Where to get |
|---|---|---|---|
| `HF_TOKEN` | ✅ | HuggingFace token for embeddings | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `GROQ_API_KEY` | ✅ | Groq API key for LLM | [console.groq.com](https://console.groq.com) — free |
| `GROQ_MODEL` | ✅ | Groq model name | `llama-3.1-8b-instant` |
| `LLM_MAX_TOKENS` | ❌ | Max tokens per response | Default: `512` |
| `EMBEDDING_MODEL` | ❌ | Sentence transformer model | Default: `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | ❌ | Text chunk size | Default: `800` |
| `CHUNK_OVERLAP` | ❌ | Chunk overlap | Default: `150` |
| `DEFAULT_TOP_K` | ❌ | Retrieved chunks per query | Default: `4` |
| `SESSION_MAX_TURNS` | ❌ | Max conversation turns kept in memory | Default: `20` |
| `ALLOWED_ORIGINS` | ❌ | Comma-separated CORS origins | Default: `http://localhost:3000` |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ingest/youtube` | Ingest a YouTube video by URL |
| `POST` | `/ingest/pdf` | Upload and ingest a PDF file |
| `POST` | `/chat` | Ask a question (session-aware) |
| `GET` | `/health` | System status and document count |
| `GET` | `/sources` | List all ingested sources this session |
| `DELETE` | `/clear` | Clear all ingested data |
| `GET` | `/docs` | Interactive Swagger UI |

---

## 🚀 Free Deployment

### Backend → [Render](https://render.com) (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo and set:

| Field | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r ../requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Python Version | `3.11` |

4. Add these environment variables in the Render dashboard:

```
HF_TOKEN=your_value
GROQ_API_KEY=your_value
GROQ_MODEL=llama-3.1-8b-instant
ALLOWED_ORIGINS=https://your-app.vercel.app
```

5. Click **Deploy** → your backend URL: `https://your-app.onrender.com`

---

### Frontend → [Vercel](https://vercel.com) (Free)

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo
2. Set:

| Field | Value |
|---|---|
| Root Directory | `frontend` |
| Framework | Create React App |

3. Add environment variable:
```
REACT_APP_API_URL=https://your-app.onrender.com
```

4. Click **Deploy** → your frontend URL: `https://your-app.vercel.app`

---

### After both are deployed

Update `ALLOWED_ORIGINS` in Render dashboard:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```
Render redeploys automatically on save.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Agent | LangGraph |
| Vector Store | FAISS (in-memory) |
| Embeddings | HuggingFace sentence-transformers |
| LLM | Groq — LLaMA 3.1 8B Instant |
| PDF parsing | PyMuPDF (in-memory, no disk write) |
| YouTube | youtube-transcript-api |
| Frontend | React 18 |

---

## 🔐 Security Notes

- `.env` is in `.gitignore` — your API keys are never pushed to GitHub
- Use `.env.example` as the template (contains no real keys)
- In production, set all secrets via Render/Vercel environment variable dashboards — never hardcode them

---

## 👤 Author

**Ijaz Ullah Khan**
KPITB AI Program

---

## 📄 License

MIT License — free to use, modify, and distribute.
