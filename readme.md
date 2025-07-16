# AI Resume Analyzer

## Overview

The **AI Resume Analyzer** is a conversational chatbot and API for intelligent candidate matching. It ingests and indexes resume files (PDF or plain text), leverages vector embeddings and RAG to match resumes against job descriptions, and provides insights through a chat interface. Designed for cost-effectiveness, it uses free-tier cloud services and open-source tools.

## Tech Stack & Free-Tier Components

* **Backend:** Python, FastAPI
* **Embedding & RAG:** LangChain, Sentence-Transformers (`all-MiniLM-L6-v2`) or Google Gemini free tier
* **PDF/Text Parsing:** `pdfplumber`, built-in Python text handling
* **Vector Storage:** Aiven PostgreSQL with `pgvector` extension or Pinecone free tier
* **LLM Service:** Google Gemini (free tier) or local open-source LLaMA
* **Orchestration:** LangChain (loaders, splitters, retrievers)
* **Storage:** Cloudflare R2 or Vercel Blob
* **Frontend:** React, Next.js (TypeScript), deployed on Vercel

---

## Core Functionality

1. **Resume Ingestion & Processing**

   * **File Support:** Upload multiple PDF and plain-text resumes.
   * **Text Extraction:** Extracts text from PDFs using `pdfplumber` and decodes text files.
   * **Chunking:** Splits content into 100–500 token chunks (with overlap) via LangChain's `RecursiveCharacterTextSplitter`.
   * **Embedding Generation:** Produces vector embeddings for each chunk using a free-tier model.

     * Recommended: Google Gemini (1.5 Flash free tier)
     * Alternative: `all-MiniLM-L6-v2` from Sentence-Transformers

2. **Vector Database Integration**

   * **Storage:** Persists embeddings in PostgreSQL with `pgvector` or in Pinecone.
   * **Retrieval:** Performs fast top-K similarity searches for job queries.

3. **RAG Chatbot & Matching**

   * **Job Description Input:** Accepts a text description of the desired role.
   * **Vector Search:** Retrieves relevant resume chunks.
   * **LLM Matching:** Uses an LLM to analyze and score candidate fit, citing context.
   * **Conversational Interface:** Supports follow-up questions for deeper candidate insights.

---

## Frontend Web UI (Bonus)

A React-based interface provides an intuitive user experience for resume uploads, semantic search, and RAG-powered chat.

**Tech Stack**

* **Framework:** React (Vite or Create React App) with TypeScript
* **Styling:** `App.css` (custom styles)
* **Components:**

  * `ResumeUpload.tsx` – Upload & monitor resume ingestion via `/upload/`.
  * `ResumeSearch.tsx` – Semantic search by skill or title via `/search/`.
  * `RAGChat.tsx` – RAG-powered chat using `/chat/` endpoint.
  * `App.tsx` – Main layout and component assembly.
* **API Module:** `api.ts` handles HTTP requests to the FastAPI backend.
* **Deployment:** Vercel (free tier) or static hosting.

**Usage**

```bash
cd frontend
npm install
npm run dev
# or for Next.js:
# npm run build && npm start
```

---

## Repository Structure

```
├── backend/
│   ├── main.py                  # FastAPI app: upload, search, chat endpoints
│   ├── resume_ingest.py         # Resume parsing, chunking, embedding logic
│   ├── db.py                    # PostgreSQL connection & vector search functions
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main React component assembling UI
│   │   ├── App.css              # Global styles (layout, buttons, inputs) fileciteturn1file0
│   │   ├── ResumeUpload.tsx     # File upload & status tracking UI fileciteturn1file4
│   │   ├── ResumeSearch.tsx     # Semantic search interface fileciteturn1file3
│   │   ├── RAGChat.tsx          # Chat interface for RAG matching fileciteturn1file2
│   │   └── api.ts               # HTTP client for backend endpoints
│   ├── package.json             # Frontend dependencies & scripts
│   └── tsconfig.json            # TypeScript configuration
└── README.md                    # Root README (this file)
```

---

## Getting Started

### Backend Setup

```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer/backend
pip install -r requirements.txt
# Configure .env from .env.example
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd ai-resume-analyzer/frontend
npm install
npm run dev
```

Visit `http://localhost:3000` (or specified port) for the web UI. Ensure the backend is running on `http://localhost:8000` or update `api.ts` accordingly.

---

---

## Deployment

* **Frontend**: Deployed on Vercel at [https://ai-resume-analyzer-1n3i.vercel.app/](https://ai-resume-analyzer-1n3i.vercel.app/)
* **Backend**: Deployed on Render at [https://ai-resume-analyzer-yhoq.onrender.com/](https://ai-resume-analyzer-yhoq.onrender.com/)

> **Note:** Despite optimizing for minimal memory usage, the Render backend frequently exceeds its free-tier memory limit and throws an “exceeded memory” error when invoking endpoints.

### Memory Optimization Efforts

* Refactored processing logic to reduce in-memory data structures.
* Streamed file parsing and chunking to lower peak RAM usage.
* Limited worker concurrency to fit within Render’s free-tier constraints.

### Asynchronous Processing Attempt

* Integrated Upstash Redis and Celery for asynchronous resume uploads and processing.
* Aimed to enqueue and handle multiple upload tasks concurrently.
* Hit the 512 MB RAM cap on Upstash free tier, leading to task failures under load.

### Database

* Used Aiven PostgreSQL with `pgvector` extension for vector storage and similarity search.

---


## Deliverables

1. **Backend System:**

   * Resume parsing, chunking, embedding, storage.
   * Vector search and RAG chatbot.
2. **Frontend Web App (Bonus):**

   * File upload UI, semantic search, and chat interface.
3. **Public GitHub Repo:**

   * Well-documented, modular code.
   * README with setup, usage, and free-tier notes.
4. **Optional:** Deployed demo on Vercel, metadata search API endpoint, and demo walkthrough.


---

*Built with open-source tools and free-tier services for cost-effective AI-powered hiring.*
