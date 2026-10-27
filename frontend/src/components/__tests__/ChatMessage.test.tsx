import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessage } from "../ChatMessage";
import { ChatMessageItem } from "../../types";

describe("ChatMessage component", () => {
  it("renders user message bubble cleanly", () => {
    const userMsg: ChatMessageItem = {
      id: "1",
      role: "user",
      content: "What is ChromaDB?",
      timestamp: "12:00 PM",
    };
    render(<ChatMessage message={userMsg} />);
    expect(screen.getByText("What is ChromaDB?")).toBeInTheDocument();
    expect(screen.getByText("12:00 PM")).toBeInTheDocument();
  });

  it("renders assistant message with Grounded badge and model tag", () => {
    const assistantMsg: ChatMessageItem = {
      id: "2",
      role: "assistant",
      content: "ChromaDB is a vector database [Source: guide.pdf, Page 1].",
      has_sufficient_evidence: true,
      model: "llama3.2:1b",
      timestamp: "12:01 PM",
      citations: [
        {
          source_filename: "guide.pdf",
          page_number: 1,
          document_id: "doc-1",
          chunk_index: 0,
        },
      ],
    };

    render(<ChatMessage message={assistantMsg} />);
    expect(screen.getByText(/ChromaDB is a vector database/)).toBeInTheDocument();
    expect(screen.getByText("Grounded in Evidence")).toBeInTheDocument();
    expect(screen.getByText("llama3.2:1b")).toBeInTheDocument();
    expect(screen.getByText("guide.pdf")).toBeInTheDocument();
    expect(screen.getByText("· Page 1")).toBeInTheDocument();
  });

  it("renders Insufficient Evidence badge when evidence is missing", () => {
    const ungroundedMsg: ChatMessageItem = {
      id: "3",
      role: "assistant",
      content: "I cannot answer this question as there is insufficient evidence.",
      has_sufficient_evidence: false,
      timestamp: "12:02 PM",
    };

    render(<ChatMessage message={ungroundedMsg} />);
    expect(screen.getByText("Insufficient Evidence")).toBeInTheDocument();
  });
});
