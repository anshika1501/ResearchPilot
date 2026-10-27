import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CitationList } from "../CitationList";
import { Citation } from "../../types";

describe("CitationList component", () => {
  const mockCitations: Citation[] = [
    {
      source_filename: "sample_paper.pdf",
      page_number: 3,
      document_id: "doc-123",
      chunk_index: 2,
    },
    {
      source_filename: "architecture.pdf",
      page_number: 7,
      document_id: "doc-456",
      chunk_index: 5,
    },
  ];

  it("renders nothing when citations list is empty", () => {
    const { container } = render(<CitationList citations={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders citations with filename and 1-based page numbers", () => {
    render(<CitationList citations={mockCitations} />);

    expect(screen.getByText("Source References (2):")).toBeInTheDocument();
    expect(screen.getByText("sample_paper.pdf")).toBeInTheDocument();
    expect(screen.getByText("· Page 3")).toBeInTheDocument();
    expect(screen.getByText("architecture.pdf")).toBeInTheDocument();
    expect(screen.getByText("· Page 7")).toBeInTheDocument();
  });

  it("invokes onSelectCitation callback when citation pill is clicked", () => {
    const onSelect = vi.fn();
    render(<CitationList citations={mockCitations} onSelectCitation={onSelect} />);

    const firstPill = screen.getByText("sample_paper.pdf").closest("button");
    expect(firstPill).not.toBeNull();
    if (firstPill) {
      fireEvent.click(firstPill);
      expect(onSelect).toHaveBeenCalledWith(mockCitations[0]);
    }
  });
});
