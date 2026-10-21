# ResearchPilot AI

ResearchPilot AI is an AI-powered document research and intelligence platform. Users upload documents, ask questions grounded in those documents, and run bounded research workflows that retrieve evidence and produce cited reports.

## Repository Organization

- **`backend/`**: FastAPI backend service, modular architecture for document ingestion, retrieval, LLM integration, and agent workflows.
- **`frontend/`**: React user interface (to be implemented in Stage 2).

## Quick Start (Backend)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Set up and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Run automated tests:
   ```bash
   pytest
   ```

For detailed setup instructions, see [`backend/README.md`](backend/README.md).
