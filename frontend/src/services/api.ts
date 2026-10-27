/**
 * API client module for ResearchPilot AI backend.
 * Uses configurable base URL and handles HTTP error responses.
 */

import {
  ChatRequest,
  ChatResponse,
  DocumentUploadResponse,
  HealthResponse,
  SearchRequest,
  SearchResponse,
} from "../types";

const getBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === "string") {
    return envUrl.replace(/\/+$/, "");
  }
  return "";
};

const BASE_URL = getBaseUrl();

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status} (${response.statusText})`;
    try {
      const errorJson = await response.json();
      if (errorJson && typeof errorJson.detail === "string") {
        errorMessage = errorJson.detail;
      } else if (errorJson && Array.isArray(errorJson.detail)) {
        errorMessage = errorJson.detail.map((d: { msg?: string }) => d.msg || "").join(", ");
      }
    } catch {
      // Non-JSON error payload
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<T>;
}

export const api = {
  /**
   * Check backend health status.
   */
  async checkHealth(): Promise<HealthResponse> {
    const url = `${BASE_URL}/api/v1/health`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    return handleResponse<HealthResponse>(res);
  },

  /**
   * Upload a PDF file for ingestion, page extraction, chunking, and vector indexing.
   */
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const url = `${BASE_URL}/api/v1/documents/upload`;
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });
    return handleResponse<DocumentUploadResponse>(res);
  },

  /**
   * Submit a question to the RAG pipeline.
   */
  async askQuestion(request: ChatRequest): Promise<ChatResponse> {
    const url = `${BASE_URL}/api/v1/chat`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(request),
    });
    return handleResponse<ChatResponse>(res);
  },

  /**
   * Perform direct semantic vector search across chunks.
   */
  async searchDocuments(request: SearchRequest): Promise<SearchResponse> {
    const url = `${BASE_URL}/api/v1/documents/search`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(request),
    });
    return handleResponse<SearchResponse>(res);
  },

  /**
   * Delete a document and its indexed vectors from ChromaDB.
   */
  async deleteDocument(
    documentId: string
  ): Promise<{ status: string; document_id: string; deleted_chunks: number }> {
    const url = `${BASE_URL}/api/v1/documents/${encodeURIComponent(documentId)}`;
    const res = await fetch(url, {
      method: "DELETE",
      headers: { Accept: "application/json" },
    });
    return handleResponse<{ status: string; document_id: string; deleted_chunks: number }>(res);
  },
};
