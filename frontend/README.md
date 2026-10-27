# ResearchPilot AI — Frontend

Modern, responsive web interface for **ResearchPilot AI**, built with **React**, **TypeScript**, **Tailwind CSS**, and **Vite**.

## Features

- **Document Management Sidebar:** View uploaded documents with page and chunk metrics; filter queries to specific documents or search across all.
- **PDF Upload Modal:** Drag-and-drop or file browser with file validation (10 MB max, PDF only), upload spinner, and indexing feedback.
- **Evidence-Grounded Chat:** Natural language Q&A grounded strictly in uploaded documents via local Ollama inference.
- **Source Citations:** Clickable citation badges displaying document filename and 1-based page number.
- **Evidence Inspector:** Expandable viewer for raw retrieved context passages with ChromaDB cosine distance scores.
- **Real-Time Backend Health Monitoring:** Live status badge tracking FastAPI backend availability.

## Tech Stack

- **Framework:** React 18 & TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Testing:** Vitest & React Testing Library

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configuration variables:
- `VITE_API_BASE_URL`: Backend API origin (e.g. `http://127.0.0.1:8000`). If omitted, requests use the Vite reverse proxy.

### 3. Start Development Server
```bash
npm run dev
```
The application will be available at [http://localhost:5173](http://localhost:5173).

### 4. Run Automated Tests
```bash
npm test
```

### 5. Build for Production
```bash
npm run build
```
Generates production assets in `dist/`.

