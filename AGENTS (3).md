# AGENTS.md — ResearchPilot AI

This file defines the project context, coding conventions, and implementation rules for AI coding agents working on ResearchPilot AI.

## 1. Project purpose

ResearchPilot AI is a document research and intelligence platform. Users upload documents, ask questions grounded in those documents, and run bounded research workflows that retrieve evidence and produce cited reports. The project is intended to demonstrate strong Python backend engineering, RAG, local LLM inference, controlled AI agents, evaluation, testing, and deployment.

Build a reliable, understandable application—not a thin wrapper around an LLM. Prefer explicit, testable components over opaque abstractions.

## 2. Planned technology stack

Use these technologies unless the repository already establishes a different decision:

- **Backend API:** FastAPI, Pydantic, Uvicorn
- **Language:** Python; use type hints for public functions and API schemas
- **Document parsing:** PyMuPDF for PDFs; reject unsupported or malformed files clearly
- **Embeddings:** Sentence Transformers with a configurable embedding model
- **Vector store:** ChromaDB, with document and page metadata
- **Local LLM inference:** Ollama through a small provider abstraction
- **Agent/RAG orchestration:** LangChain only where it adds clear value; keep retrieval and agent logic understandable and independently testable
- **Relational data:** PostgreSQL for users, document metadata, conversations, jobs, and audit records
- **Background jobs:** Celery and Redis when asynchronous indexing or research tasks are introduced
- **Frontend:** React; keep frontend implementation separate from backend business logic
- **Testing:** pytest, FastAPI TestClient or HTTPX, and deterministic mocks for external model calls
- **Packaging and deployment:** Docker, Docker Compose, GitHub Actions

Pin dependencies in the project's chosen dependency-management files. Check the existing repository before introducing or replacing tools. Do not add every planned technology in the first milestone.

## 3. Core product capabilities

Implement capabilities incrementally:

1. Upload PDF and plain-text documents with size and type validation.
2. Extract text while preserving page numbers and useful source metadata.
3. Normalize extracted text and split it into configurable, overlapping chunks.
4. Generate embeddings and store chunks in ChromaDB with stable IDs and metadata.
5. Retrieve relevant chunks for a query, with optional metadata filters.
6. Generate answers using a configured LLM and return source citations.
7. Support multiple documents and document-level access boundaries.
8. Expose validated FastAPI endpoints for document management, questions, and research jobs.
9. Add a bounded research agent with explicitly registered tools, a maximum step count, timeouts, and structured results.
10. Evaluate retrieval and answer quality; compare prompt, chunking, embedding, and model configurations.
11. Add a small Hugging Face/PyTorch fine-tuning experiment as a separate, reproducible learning module—not as a prerequisite for basic RAG.
12. Package the services for local development and deployment.

## 4. Architecture and code organization

Prefer separation of concerns. A suggested structure is:

```text
researchpilot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app and router registration
│   │   ├── core/                   # Settings, logging, security
│   │   ├── api/                    # HTTP routes and dependency injection
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── models/                 # Relational ORM models, if used
│   │   ├── services/               # Application use cases
│   │   ├── ingestion/              # Parsing, normalization, chunking
│   │   ├── retrieval/              # Embeddings, vector store, retrievers
│   │   ├── llm/                    # Provider interfaces and Ollama adapter
│   │   ├── agents/                 # Agent state, tools, bounded execution
│   │   └── db/                     # Database session and repositories
│   ├── tests/
│   ├── pyproject.toml              # Or the dependency file already in use
│   └── Dockerfile
├── frontend/
├── evaluation/                     # Versioned datasets and evaluation scripts
├── scripts/                        # Local setup and maintenance scripts
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

Treat this as a guide, not a mandate to create empty folders. Follow established repository structure when one exists. Avoid giant modules and circular imports. Keep route handlers thin; put business logic in services.

## 5. Engineering rules

- Inspect the repository, existing instructions, dependency files, and tests before editing.
- Make the smallest coherent change that solves the task. Do not rewrite unrelated code.
- Use clear names, type hints, focused functions, and docstrings for non-obvious behavior.
- Keep configuration in environment variables/settings, never hard-code credentials, tokens, hostnames, or machine-specific paths.
- Maintain `.env.example` with safe placeholders only. Never commit `.env` or real secrets.
- Use structured logging; never log passwords, API keys, full private documents, or sensitive user data.
- Validate input at API boundaries and return useful, non-sensitive error responses.
- Use dependency injection for database sessions and model/provider clients where practical.
- Add or update tests for each behavior change. Do not claim tests passed unless they were actually run.
- Run focused tests first, then the broader test suite when feasible. Report commands run and any limitations.
- Do not silently swallow exceptions. Catch expected errors at the appropriate boundary and preserve useful diagnostic context in logs.
- Avoid unnecessary abstractions, speculative features, and dependencies that duplicate existing functionality.
- Never fabricate evaluation scores, benchmark results, citations, or implementation claims.

## 6. RAG and document ingestion requirements

### Ingestion

- Validate file extension, MIME type where available, and file size; do not trust the filename alone.
- Treat document contents as untrusted input. Text inside a PDF must never override system instructions or grant tool permissions.
- Extract page-aware text and retain metadata such as document ID, page number, chunk index, and source filename.
- Handle scanned/image-only PDFs gracefully: report that OCR is needed rather than silently indexing empty content. OCR can be added as an optional later capability.
- Normalize whitespace conservatively; do not destroy meaningful tables, headings, or paragraph boundaries without a reason.
- Make chunk size and overlap configurable. Keep chunking deterministic and unit-tested.
- Use stable chunk IDs or an explicit replacement strategy so re-uploading a document does not create duplicate chunks indefinitely.
- Make deletion remove the relevant vectors and metadata, subject to the application's documented retention policy.

### Retrieval and answers

- Keep retrieval separate from generation so each can be tested and tuned independently.
- Include source metadata in retrieval results and return citations that map to real document/page/chunk records.
- If evidence is missing or weak, say so; do not invent an answer or citation.
- Do not treat a high similarity score as proof that a claim is correct.
- Support a configurable top-k and metadata filtering. Avoid retrieving more context than the model can reasonably use.
- Consider prompt-injection content in retrieved documents untrusted. Retrieved text is evidence, not instructions.
- Test questions with relevant evidence, no evidence, conflicting evidence, and malicious instructions embedded in documents.

## 7. LLM and prompt requirements

- Route all model calls through a small provider interface so the application can switch models without changing business logic.
- Keep model names, base URLs, generation settings, and timeouts configurable.
- Set sensible timeouts and handle model unavailability, malformed output, and resource exhaustion.
- Ask for structured output when downstream code depends on a schema, then validate it with Pydantic or equivalent validation.
- Separate system instructions from user input and retrieved document content.
- Do not promise that prompt engineering alone guarantees safety or correctness.
- Keep prompts versioned or centrally managed; write tests for important output contracts.
- Avoid sending document content to external providers unless the configuration and user-facing behavior explicitly allow it.

## 8. Agent safety and reliability

Agents must be bounded, observable, and predictable enough to test.

- Give the agent only explicitly registered tools with narrow input schemas and documented effects.
- Begin with read-only tools: search uploaded documents, fetch selected passages, summarize evidence, and compare sources.
- Do not add shell execution, arbitrary Python execution, unrestricted filesystem access, or unrestricted network browsing as agent tools.
- Enforce a maximum number of steps, per-tool timeouts, overall task deadlines, and output size limits.
- Validate tool arguments and tool results. Handle unknown tools and malformed arguments safely.
- Require evidence references for research conclusions and distinguish sourced facts from analysis or uncertainty.
- Treat user instructions and retrieved content as untrusted; neither may expand tool permissions.
- Require explicit user confirmation before any future consequential external action, if such actions are added.
- Record task status, selected tools, durations, and errors without logging secrets or unnecessarily storing raw sensitive content.
- Make agent runs cancellable where background execution is supported, and ensure failures produce a clear terminal state.

## 9. API design

- Use versioned routes when the API begins to have external consumers (for example, `/api/v1`).
- Use Pydantic schemas for all request and response bodies; do not expose ORM objects directly.
- Use appropriate HTTP status codes and consistent error response shapes.
- Validate upload sizes, query length, pagination bounds, and task parameters.
- Keep long-running indexing and research operations asynchronous when needed; return a job ID and provide a way to check status.
- Apply authentication and authorization before exposing user-specific documents or conversations.
- Ensure every database query and vector search respects the current user's document access scope.
- Do not use synchronous blocking model calls directly in async routes if they can block the event loop; use async clients or an appropriate worker/thread strategy.

## 10. Security and privacy

- Use least privilege for database users and container services.
- Never commit credentials or expose secrets in API responses, logs, screenshots, or test fixtures.
- Enforce document ownership/tenant boundaries in both relational queries and vector retrieval.
- Protect against oversized uploads, path traversal, malicious filenames, unsafe deserialization, and resource-exhaustion inputs.
- Do not execute uploaded files. Treat extracted text and model outputs as untrusted.
- Add rate limits and quotas before exposing the service publicly.
- Configure CORS narrowly for the intended frontend origin; do not use permissive production defaults without a reason.
- Use HTTPS and secure secret management in deployed environments.
- Keep private documents local by default when using Ollama. Clearly document any optional external-model integration.

## 11. Testing and evaluation

Maintain both software tests and AI-quality evaluations; they solve different problems.

### Software tests

- Unit-test parsing, text normalization, chunking, metadata, prompt construction, and citation mapping.
- Test API validation, authentication, authorization, upload limits, and error handling.
- Mock LLM and embedding clients in normal unit tests so the suite is deterministic and does not require downloaded models or a running Ollama service.
- Add integration tests for PostgreSQL/ChromaDB only when the required services are available.
- Test that a user's query cannot retrieve another user's documents.
- Test malicious instructions in uploaded documents and tool output.

### AI evaluation

- Keep a small, versioned evaluation dataset with questions, expected evidence, and expected-answer criteria.
- Track retrieval relevance/recall where labels are available, citation correctness, answer correctness/groundedness, latency, failures, and resource use.
- Compare configurations on the same dataset and hardware where possible.
- Record model version, embedding model, chunking configuration, prompt version, and environment with each run.
- Report limitations and sample sizes. Never claim a metric without reproducible evidence.

## 12. Local development and deployment

- Document prerequisites and exact setup commands in the README.
- Provide Docker Compose for services that are actually implemented; do not require every planned service from day one.
- Add health checks and clear startup/readiness behavior.
- Keep model downloads and persistent data in documented volumes; avoid baking large model weights into the application image unless there is a clear reason.
- Document RAM, disk, and GPU expectations for selected local models. Provide a smaller-model fallback for limited hardware.
- Ensure the core API can start and its tests can run without requiring a GPU.
- Add CI that installs dependencies, runs formatting/linting if configured, and executes tests.
- Never deploy with debug mode, development credentials, or open administrative ports enabled.

## 13. Suggested implementation order

1. Inspect the repository and write a concise implementation plan.
2. Set up the FastAPI app, configuration, health endpoint, and pytest.
3. Implement PDF/text parsing and deterministic chunking.
4. Add embedding generation and ChromaDB storage behind interfaces.
5. Implement retrieval and citation-aware answer generation with a mocked provider test path.
6. Add PostgreSQL persistence and document ownership checks.
7. Add upload/question APIs and robust validation.
8. Add the bounded, read-only research agent and task-status flow.
9. Create the evaluation dataset and benchmark scripts.
10. Add the small fine-tuning experiment if core capabilities are stable.
11. Containerize, add CI, and finish setup/security documentation.

After each step, summarize files changed, decisions made, tests run, and the next recommended step. Ask before making a broad architectural change or adding a costly/external dependency.

## 14. Definition of done

A feature is complete when:

- The behavior matches the task and is documented where appropriate.
- Inputs and failure cases are handled explicitly.
- Relevant tests are added or updated and have been run, with results reported honestly.
- Security, privacy, ownership, and resource limits have been considered.
- Configuration and dependencies are documented without exposing secrets.
- AI output is not presented as verified fact without supporting evidence.
- The README and `.env.example` are updated when setup or configuration changes.

## 15. Agent response style

When working on this repository:

1. Inspect before editing; do not assume files or dependencies exist.
2. Explain the approach briefly before substantial changes.
3. Implement working code rather than only describing it when asked to build a feature.
4. Prefer small, verifiable milestones.
5. Report actual test results and unresolved limitations.
6. Do not invent files, commands, deployment status, model results, or completed work.
