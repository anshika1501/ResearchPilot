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
│   │   └── health.py
│   ├── ingestion/              # Document parsing, normalization, chunking (future)
│   ├── retrieval/              # Vector stores, embeddings, retrieval logic (future)
│   ├── llm/                    # Local LLM (Ollama) provider interface (future)
│   ├── agents/                 # Research agent workflows and tools (future)
│   ├── services/               # Core business services
│   ├── models/                 # Database ORM models (future)
│   └── db/                     # Database sessions and repositories (future)
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures and test client
│   └── test_health.py          # Health check endpoint tests
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

### 6. Run Automated Tests
```bash
pytest
```
