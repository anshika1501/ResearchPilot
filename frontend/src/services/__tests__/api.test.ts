import { describe, it, expect, vi, beforeEach } from "vitest";
import { api } from "../api";

describe("api client service", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("checkHealth fetches /api/v1/health and returns JSON", async () => {
    const mockHealth = {
      status: "ok",
      app_name: "ResearchPilot AI",
      version: "0.1.0",
      environment: "development",
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealth,
    } as unknown as Response);

    const result = await api.checkHealth();
    expect(result).toEqual(mockHealth);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/health"),
      expect.any(Object)
    );
  });

  it("uploadDocument posts FormData to /documents/upload", async () => {
    const mockUploadResponse = {
      document_id: "doc-123",
      filename: "test.pdf",
      file_size_bytes: 1024,
      page_count: 1,
      total_chunks: 2,
      pages: [],
      chunks: [],
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockUploadResponse,
    } as unknown as Response);

    const testFile = new File(["dummy content"], "test.pdf", { type: "application/pdf" });
    const result = await api.uploadDocument(testFile);

    expect(result.document_id).toBe("doc-123");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/documents/upload"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("askQuestion posts ChatRequest and returns ChatResponse", async () => {
    const mockChatResponse = {
      question: "What is AI?",
      answer: "AI is artificial intelligence [Source: intro.pdf, Page 1].",
      citations: [],
      evidence: [],
      has_sufficient_evidence: true,
      model: "llama3.2:1b",
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockChatResponse,
    } as unknown as Response);

    const result = await api.askQuestion({ question: "What is AI?", top_k: 3 });
    expect(result.answer).toContain("AI is artificial intelligence");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/chat"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ question: "What is AI?", top_k: 3 }),
      })
    );
  });

  it("throws extracted detail error on HTTP failure", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({ detail: "Invalid file type. Only PDF files are supported." }),
    } as unknown as Response);

    const testFile = new File(["notes"], "notes.txt", { type: "text/plain" });
    await expect(api.uploadDocument(testFile)).rejects.toThrow(
      "Invalid file type. Only PDF files are supported."
    );
  });
});
