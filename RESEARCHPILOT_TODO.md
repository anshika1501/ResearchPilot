# ResearchPilot AI — Project Roadmap & To-Do List

## Project goal

Build a research assistant that can read multiple PDFs, answer questions using evidence from those documents, and run a controlled AI research workflow that produces a report with citations.

**Build in three stages.** Finish and test each stage before moving to the next. Start with a simple working version; add complexity only when the earlier stage is reliable.

## The project at a glance

**User uploads documents → text is extracted → text is split into chunks → embeddings are stored → relevant chunks are retrieved → an LLM answers with citations → an agent can use these capabilities to complete a research task → results are evaluated and the app is deployed.**

### Suggested stack

- Backend API: FastAPI
- PDF extraction: PyMuPDF
- Embeddings: Sentence Transformers
- Vector store: ChromaDB
- Local LLM inference: Ollama
- Application data: PostgreSQL
- Frontend: React (add after the API works)
- Testing: pytest
- Packaging: Docker / Docker Compose
- Later learning: LangChain and PyTorch/Hugging Face fine-tuning

Keep the first version small. Use one embedding model and one local LLM initially; do not add every library at once.

---

# Stage 1 — Build the Foundation and a Working RAG App

**Goal:** A user can upload a PDF, ask a question about it, and receive an answer grounded in the PDF with source references.

## A. Understand the flow
- [ ] Read the basics of embeddings, chunking, vector similarity search, and RAG.
- [ ] Draw a simple architecture diagram before coding.
- [ ] Decide what counts as a successful answer: relevant evidence, a useful response, and a correct source reference.

## B. Set up the project
- [x] Create a Git repository and a clear project folder structure.
- [x] Create and activate a Python virtual environment.
- [x] Add a dependency file and install only the packages needed for Stage 1.
- [x] Add `.env.example` and `.gitignore`; never commit secrets or uploaded private documents.
- [x] Create the FastAPI app and a `/health` endpoint.
- [x] Add initial pytest tests and a README with setup instructions.

## C. Implement document ingestion
- [ ] Create an endpoint to upload PDF files.
- [ ] Validate file type and file size; return helpful errors for invalid or empty PDFs.
- [ ] Extract text page by page with PyMuPDF.
- [ ] Keep document name and page number as metadata.
- [ ] Split extracted text into chunks with a configurable size and overlap.
- [ ] Add tests for valid PDFs, empty PDFs, invalid file types, and extraction errors.

## D. Add embeddings and retrieval
- [ ] Generate embeddings using a Sentence Transformers model.
- [ ] Store chunks, embeddings, and metadata in ChromaDB.
- [ ] Implement a search function that retrieves the most relevant chunks for a question.
- [ ] Return the source document and page number for every retrieved chunk.
- [ ] Test retrieval with questions whose answers are present in the PDF and questions whose answers are absent.

## E. Generate grounded answers
- [ ] Install and run Ollama with a model that fits the computer's resources.
- [ ] Send the question and retrieved context to the model.
- [ ] Write a prompt that instructs the model to answer from supplied evidence and say when the evidence is insufficient.
- [ ] Return the answer and citations in a consistent JSON response.
- [ ] Test that citations map to actual retrieved pages and that unsupported questions are handled honestly.

## Stage 1 completion checklist
- [ ] A fresh setup works using only the README instructions.
- [ ] Upload → extraction → chunking → embedding → retrieval → answer works end to end.
- [ ] Automated tests pass.
- [ ] Answers include source references and do not pretend to know information absent from the documents.
- [ ] Record known limitations in the README.

**Do not move to Stage 2 until this flow works reliably.**

---

# Stage 2 — Turn RAG into a Useful Research Application

**Goal:** Support multiple documents and users, provide a clean API, and let a controlled AI agent complete multi-step research tasks.

## A. Improve the backend
- [ ] Organize code into separate modules for API routes, schemas, configuration, ingestion, retrieval, generation, and services.
- [ ] Add Pydantic request and response schemas.
- [ ] Add consistent error handling, logging, and request validation.
- [ ] Store document metadata, conversations, and research tasks in PostgreSQL.
- [ ] Add document listing and deletion; ensure deleted documents are also removed from the vector store.
- [ ] Add authentication and enforce that users can access only their own documents.
- [ ] Add background processing for long document-ingestion jobs if needed.

## B. Support multiple documents
- [ ] Let users upload and query multiple PDFs together.
- [ ] Add metadata filters so a user can search selected documents.
- [ ] Prevent duplicate ingestion or define how duplicate uploads are handled.
- [ ] Improve chunking and retrieval based on tests, not guesswork.
- [ ] Make citations identify the document and page clearly.

## C. Build the research agent
- [ ] Define one bounded use case: compare reports and produce an evidence-based summary.
- [ ] Create small tools such as `search_documents`, `summarize_passages`, and `compare_evidence`.
- [ ] Use LangChain or another framework only where it helps; keep tool functions understandable and testable.
- [ ] Define a workflow: understand task → plan → retrieve evidence → analyze → check evidence → write report.
- [ ] Limit the number of steps, tool calls, execution time, and output size.
- [ ] Validate tool inputs and outputs; handle tool failures without crashing.
- [ ] Require citations for factual findings and flag missing or conflicting evidence.
- [ ] Treat uploaded document text as untrusted data, not as instructions for the agent.
- [ ] Save task status and the final report so the user can inspect the result.

## D. Add a simple interface
- [ ] Build a React interface for uploading documents and viewing ingestion status.
- [ ] Add a chat screen with answers and clickable source references.
- [ ] Add a research-task form and a report/results screen.
- [ ] Show loading, empty, and error states clearly.
- [ ] Keep the interface focused on demonstrating the AI workflow rather than adding decorative features.

## Stage 2 completion checklist
- [ ] Users can manage their own documents securely.
- [ ] Questions can search across selected documents.
- [ ] The research agent uses tools and stops within defined limits.
- [ ] Reports distinguish supported findings from missing evidence and include citations.
- [ ] API and agent tests cover success cases, invalid inputs, missing evidence, and tool failures.
- [ ] The main user flow works through the interface.

**Do not add unrestricted web browsing or many agents yet. A single reliable agent is enough.**

---

# Stage 3 — Evaluate, Optimize, and Deploy

**Goal:** Prove the system works, understand its trade-offs, and package it like a portfolio-quality application.

## A. Create an evaluation set
- [ ] Collect a small set of sample PDFs that you are allowed to use.
- [ ] Write test questions, expected answers, and expected supporting pages.
- [ ] Include answerable questions, unanswerable questions, and questions requiring comparison across documents.
- [ ] Measure retrieval quality, citation correctness, answer quality, and response time.
- [ ] Keep baseline results so later improvements can be compared fairly.

## B. Optimize with evidence
- [ ] Compare a few chunk sizes and overlap values.
- [ ] Compare retrieval settings such as top-k and metadata filters.
- [ ] Try a prompt change and compare results against the baseline.
- [ ] Compare two compatible models if computer resources allow.
- [ ] Record latency, memory use, and quality; do not claim improvements without measurements.
- [ ] Add caching only where it is safe and useful.
- [ ] Profile slow operations before attempting complicated optimization.

## C. Complete one ML learning experiment
- [ ] Use Hugging Face Transformers and PyTorch to fine-tune a small pretrained text classifier on a suitable public dataset.
- [ ] Split data into training, validation, and test sets without leakage.
- [ ] Compare the baseline model with the fine-tuned model.
- [ ] Report accuracy and macro F1, explain limitations, and save the experiment instructions.
- [ ] Keep this experiment separate from the RAG pipeline unless there is a clear reason to integrate it.

## D. Make it deployable
- [ ] Add Docker configuration for the backend and required services.
- [ ] Add Docker Compose for local development where practical.
- [ ] Configure environment variables and keep secrets out of Git.
- [ ] Add health checks, structured logs, and clear startup/shutdown behavior.
- [ ] Configure CI to run tests and basic code checks on pushes or pull requests.
- [ ] Document model download/setup, storage, resource requirements, and common errors.
- [ ] Test the complete application from a clean environment.
- [ ] Deploy only to an environment with enough memory/compute for the chosen model; document if Ollama runs separately.

## E. Prepare the portfolio and interview story
- [ ] Update the README with the problem, features, architecture diagram, setup steps, API examples, and screenshots.
- [ ] Add a short demo showing upload → question → citations → research report.
- [ ] Document design choices, trade-offs, limitations, and future improvements.
- [ ] Prepare to explain RAG, embeddings, vector search, agents, tool calling, prompt optimization, fine-tuning, evaluation, and deployment.
- [ ] Include only features that genuinely work; distinguish completed work from planned work.

## Stage 3 completion checklist
- [ ] Evaluation results are reproducible and documented.
- [ ] At least one optimization is supported by measured results.
- [ ] The small fine-tuning experiment is documented, if computer resources permit.
- [ ] Docker/CI and setup instructions work from a clean checkout.
- [ ] The repository is presentable and the demo can be explained clearly.

---

## Recommended build order

1. FastAPI health endpoint and tests.
2. PDF text extraction.
3. Chunking and metadata.
4. Embeddings and ChromaDB retrieval.
5. Ollama answer generation with citations.
6. End-to-end RAG tests.
7. PostgreSQL, user/document management, and React UI.
8. One controlled research agent.
9. Evaluation and optimization.
10. Fine-tuning experiment, Docker, CI, and portfolio polish.

## Working rules

- Make small changes and run tests after each milestone.
- Keep functions focused and add type hints where useful.
- Never commit API keys, passwords, or private documents.
- Do not claim model accuracy or speed improvements without measurement.
- Prefer a simple, understandable implementation over unnecessary abstractions.
- Ask the coding assistant to explain files and decisions, not just generate code.
- Update this checklist as tasks are completed.

## Definition of done

ResearchPilot AI is complete enough for a portfolio when a reviewer can follow the setup instructions, upload sample PDFs, ask questions with verifiable citations, run a bounded research task, inspect evaluation results, and understand how the system is tested and deployed.
