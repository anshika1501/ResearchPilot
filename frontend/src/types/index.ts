/**
 * TypeScript types and interfaces matching the FastAPI backend schemas.
 */

export interface ExtractedPage {
  page_number: number;
  text: string;
  char_count: number;
}

export interface DocumentChunk {
  chunk_index: number;
  text: string;
  page_number: number;
  source_filename: string;
  metadata: Record<string, unknown>;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  total_chunks: number;
  pages: ExtractedPage[];
  chunks: DocumentChunk[];
}

export interface Citation {
  source_filename: string;
  page_number: number;
  document_id: string;
  chunk_index: number;
}

export interface EvidencePassage {
  text: string;
  source_filename: string;
  page_number: number;
  document_id: string;
  chunk_index: number;
  distance: number;
}

export interface ChatRequest {
  question: string;
  document_id?: string;
  top_k?: number;
}

export interface ChatResponse {
  question: string;
  answer: string;
  citations: Citation[];
  evidence: EvidencePassage[];
  has_sufficient_evidence: boolean;
  model: string;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  document_id?: string;
}

export interface SearchResult {
  text: string;
  source_filename: string;
  page_number: number;
  chunk_index: number;
  document_id: string;
  distance: number;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
}

export interface UploadedDocumentRecord {
  document_id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  total_chunks: number;
  uploaded_at: string;
}

export interface ChatMessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  evidence?: EvidencePassage[];
  has_sufficient_evidence?: boolean;
  model?: string;
  timestamp: string;
}
