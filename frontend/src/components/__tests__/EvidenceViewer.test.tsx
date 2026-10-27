import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceViewer } from "../EvidenceViewer";
import { EvidencePassage } from "../../types";

describe("EvidenceViewer component", () => {
  const mockEvidence: EvidencePassage[] = [
    {
      text: "Dense vector retrieval maps unstructured text into high-dimensional space.",
      source_filename: "vectors.pdf",
      page_number: 2,
      chunk_index: 0,
      document_id: "doc-1",
      distance: 0.182,
    },
  ];

  it("renders collapsed header showing passage count", () => {
    render(<EvidenceViewer evidence={mockEvidence} />);
    expect(screen.getByText("Retrieved Evidence Passages (1)")).toBeInTheDocument();
    expect(screen.queryByText(/Dense vector retrieval maps/)).not.toBeInTheDocument();
  });

  it("expands on click to display passage excerpt, page, and distance score", () => {
    render(<EvidenceViewer evidence={mockEvidence} />);
    const toggleButton = screen.getByRole("button");
    fireEvent.click(toggleButton);

    expect(screen.getByText("vectors.pdf")).toBeInTheDocument();
    expect(screen.getByText("· Page 2")).toBeInTheDocument();
    expect(screen.getByText("dist: 0.182")).toBeInTheDocument();
    expect(screen.getByText(/Dense vector retrieval maps/)).toBeInTheDocument();
  });
});
