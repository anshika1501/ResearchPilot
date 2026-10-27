"""Deterministic text chunking module with configurable size and overlap."""

from typing import Optional
from app.core.config import settings
from app.schemas.documents import DocumentChunk, ExtractedPage


class TextChunker:
    """Deterministic text chunker that splits document pages into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> None:
        self.chunk_size = (
            chunk_size if chunk_size is not None else settings.DEFAULT_CHUNK_SIZE
        )
        self.chunk_overlap = (
            chunk_overlap if chunk_overlap is not None else settings.DEFAULT_CHUNK_OVERLAP
        )

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate chunk size and overlap configurations."""
        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {self.chunk_overlap}")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap must be strictly less than chunk_size ({self.chunk_overlap} >= {self.chunk_size})"
            )

    def chunk_text(
        self,
        text: str,
        page_number: int,
        source_filename: str,
        start_chunk_index: int = 0,
    ) -> list[DocumentChunk]:
        """Split a string of text into deterministic overlapping chunks.

        Args:
            text: Text to be chunked.
            page_number: 1-based page number where this text originated.
            source_filename: Source file name for citation tracking.
            start_chunk_index: Base index for sequential chunk numbering.

        Returns:
            A list of DocumentChunk models preserving source and page metadata.
        """
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        if len(cleaned_text) <= self.chunk_size:
            return [
                DocumentChunk(
                    chunk_index=start_chunk_index,
                    text=cleaned_text,
                    page_number=page_number,
                    source_filename=source_filename,
                    metadata={"char_start": 0, "char_end": len(cleaned_text)},
                )
            ]

        chunks: list[DocumentChunk] = []
        step = self.chunk_size - self.chunk_overlap
        current_idx = start_chunk_index
        text_length = len(cleaned_text)
        start = 0

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_content = cleaned_text[start:end]

            chunks.append(
                DocumentChunk(
                    chunk_index=current_idx,
                    text=chunk_content,
                    page_number=page_number,
                    source_filename=source_filename,
                    metadata={"char_start": start, "char_end": end},
                )
            )
            current_idx += 1
            start += step

        return chunks

    def chunk_pages(
        self,
        pages: list[ExtractedPage],
        source_filename: str,
    ) -> list[DocumentChunk]:
        """Split multiple pages into continuous sequential chunks while preserving page boundaries.

        Args:
            pages: List of extracted document pages.
            source_filename: Source filename for metadata tracking.

        Returns:
            A list of DocumentChunk models across all pages.
        """
        all_chunks: list[DocumentChunk] = []
        current_chunk_index = 0

        for page in pages:
            page_chunks = self.chunk_text(
                text=page.text,
                page_number=page.page_number,
                source_filename=source_filename,
                start_chunk_index=current_chunk_index,
            )
            all_chunks.extend(page_chunks)
            current_chunk_index = len(all_chunks)

        return all_chunks
