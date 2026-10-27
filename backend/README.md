# ResearchPilot AI — Backend

Backend API service for **ResearchPilot AI**, built with Python and FastAPI.

## Directory Structure

```text
backend/
├── app/
│   ├── main.py                 # FastAPI application initialization & root routes
│   ├── core/                   # Application configuration, settings, logging
│   │   ├── __init__.py
│   │   └── config.py
│   ├── api/                    # API route definitions
│   │   └── v1/
│   │       ├── api.py          # Version 1 router aggregator
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py   # Health check route handler
│   ├── schemas/                # Pydantic data schemas
│   │   ├── __init__.py
│   │   ├── chat.py             # RAG question and answer schemas
│   │   ├── documents.py        # Document ingestion and chunking schemas
│   │   └── health.py
│   ├── ingestion/              # Document parsing, normalization, chunking
│   │   ├── __init__.py
│   │   ├── chunker.py          # Deterministic text chunker
│   │   ├── exceptions.py       # Custom ingestion exceptions
│   │   └── pdf_parser.py       # PyMuPDF-based PDF extraction service
│   ├── retrieval/              # Vector stores, embeddings, retrieval logic
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Sentence Transformers embedding service
│   │   ├── exceptions.py       # Retrieval and vector store exceptions
│   │   └── vector_store.py     # ChromaDB collection management and search
│   ├── llm/                    # Local LLM (Ollama) provider interface
│   │   ├── __init__.py
│   │   ├── exceptions.py       # Ollama provider exceptions
│   │   ├── ollama_client.py    # Local HTTP API client for Ollama
│   │   └── prompts.py          # Grounded RAG prompt templates
│   ├── agents/                 # Research agent workflows and tools (future)
│   ├── services/               # Core business services
│   │   ├── __init__.py
│   │   └── rag_service.py      # End-to-end RAG orchestrator service
│   ├── models/                 # Database ORM models (future)
│   └── db/                     # Database sessions and repositories (future)
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures and test client
│   ├── test_chat_api.py        # RAG /chat endpoint integration tests
│   ├── test_chunker.py         # Text chunking unit tests
│   ├── test_documents_api.py   # Document upload API integration tests
│   ├── test_documents_search_api.py # Semantic search integration tests
│   ├── test_health.py          # Health check endpoint tests
│   ├── test_ollama_client.py   # Ollama HTTP client unit tests
│   ├── test_pdf_parser.py      # PDF parsing and extraction tests
│   ├── test_prompts.py         # Prompt template unit tests
│   ├── test_rag_service.py     # RAG orchestration service unit tests
│   └── test_retrieval.py       # Vector store and embedding unit tests
├── .env.example                # Environment configuration template
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

## Setup Instructions

### 1. Prerequisites
- Python 3.11+ (Python 3.13 supported)

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Run the Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The interactive API documentation is available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) or [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### 6. Test Document Upload Endpoint

You can test the document ingestion endpoint with `curl` or PowerShell:

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

**PowerShell:**
```powershell
$form = @{
    file = Get-Item -Path "path\to\your\document.pdf"
}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/upload" -Method Post -Form $form
```

**Response Format:**
```json
{
  "filename": "document.pdf",
  "file_size_bytes": 102400,
  "page_count": 3,
  "total_chunks": 5,
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text content...",
      "char_count": 450
    }
  ],
  "chunks": [
    {
      "chunk_index": 0,
      "text": "Chunk text content...",
      "page_number": 1,
      "source_filename": "document.pdf",
      "metadata": {
        "char_start": 0,
        "char_end": 500
      }
    }
  ]
}
```

### 7. Test Semantic Search Endpoint

After uploading a document, query the indexed chunks using natural language:

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "evidence and methodology", "top_k": 3}'
```

**PowerShell:**
```powershell
$body = @{
    query = "evidence and methodology"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/documents/search" -Method Post -Body $body -ContentType "application/json"
```

**Response Format:**
```json
{
  "query": "evidence and methodology",
  "results": [
    {
      "text": "Extracted text chunk containing relevant evidence...",
      "source_filename": "document.pdf",
      "page_number": 2,
      "chunk_index": 3,
      "document_id": "c71a39f0-2f63-44b2-9d32-d17e6fa0342b",
      "distance": 0.281,
      "metadata": {
        "char_start": 450,
        "char_end": 950
      }
    }
  ],
  "total_results": 1
}
```

> **Interpreting ChromaDB Distance:** ChromaDB uses cosine distance ($[0, 2]$) by default. **Smaller distance values indicate greater semantic similarity** (0 means identical vector). Distance scores represent metric separation in embedding space and must **not** be interpreted as probabilities or confidence percentages.

### 8. Embedding Model Details

- **Default Model:** `all-MiniLM-L6-v2` (`sentence-transformers/all-MiniLM-L6-v2`)
- **Dimension:** 384 dimensions
- **Resource Footprint:** ~80 MB model weights, ~100 MB RAM runtime overhead
- **Hardware Requirement:** Fast execution on standard x86_64/ARM CPUs; GPU optional but not required.

### 9. Local Ollama Setup & LLM Configuration

ResearchPilot uses **Ollama** for local, offline LLM inference.

1. **Install Ollama:**
   - Download and install Ollama from [https://ollama.com](https://ollama.com).

2. **Pull a Model:**
   For lightweight development, pull `llama3.2:1b` (1.3 GB) or `llama3.2:3b` (2.0 GB):
   ```bash
   ollama pull llama3.2:1b
   ```

3. **Verify Ollama is Running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Configuration (`.env`):**
   ```env
   OLLAMA_BASE_URL="http://localhost:11434"
   OLLAMA_MODEL="llama3.2:1b"
   OLLAMA_TIMEOUT_SECONDS=30.0
   LLM_TEMPERATURE=0.1
   ```

---

### 10. Test Grounded RAG Question Answering (`/chat`)

Send a question grounded in your uploaded documents:

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the primary methodology described in the report?", "top_k": 3}'
```

**PowerShell:**
```powershell
$body = @{
    question = "What is the primary methodology described in the report?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/chat" -Method Post -Body $body -ContentType "application/json"
```

**Response Format:**
```json
{
  "question": "What is the primary methodology described in the report?",
  "answer": "The methodology uses dense semantic vectors and ChromaDB indexing [Source: report.pdf, Page 1].",
  "citations": [
    {
      "source_filename": "report.pdf",
      "page_number": 1,
      "document_id": "c71a39f0-2f63-44b2-9d32-d17e6fa0342b",
      "chunk_index": 0
    }
  ],
  "evidence": [
    {
      "text": "The methodology relies on dense vectors...",
      "source_filename": "report.pdf",
      "page_number": 1,
      "document_id": "c71a39f0-2f63-44b2-9d32-d17e6fa0342b",
      "chunk_index": 0,
      "distance": 0.18
    }
  ],
  "has_sufficient_evidence": true,
  "model": "llama3.2:1b"
}
```

---

### 11. Known Limitations (Stage 1)

- **Scanned Documents & OCR:** Ingestion rejects scanned/image-only PDFs where text cannot be extracted, requiring future OCR support.
- **Relational Metadata Persistence:** ChromaDB stores vector chunks and metadata, but user authentication, relational metadata persistence (PostgreSQL), and background job workers are scheduled for Stage 2.
- **Single Context Window:** The prompt includes top-k retrieved passages. For extremely large multi-document syntheses, bounded AI agents with iterative retrieval will be introduced in Stage 2.

---

### 12. Run Automated Tests
```bash
pytest
```
