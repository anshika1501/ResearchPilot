"""Unit tests for deterministic text chunking."""

import pytest
from app.ingestion.chunker import TextChunker
from app.schemas.documents import ExtractedPage


def test_chunk_short_text():
    """Text shorter than chunk_size should produce exactly one chunk."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "Short sentence under 100 characters."

    chunks = chunker.chunk_text(
        text=text,
        page_number=1,
        source_filename="test.pdf",
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == text
    assert chunks[0].page_number == 1
    assert chunks[0].source_filename == "test.pdf"


def test_chunk_empty_text():
    """Empty or whitespace-only text should produce zero chunks."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    chunks_empty = chunker.chunk_text("", page_number=1, source_filename="test.pdf")
    assert chunks_empty == []

    chunks_whitespace = chunker.chunk_text("   \n\t  ", page_number=1, source_filename="test.pdf")
    assert chunks_whitespace == []


def test_chunk_long_text_deterministic_overlap():
    """Long text should be split into deterministic chunks with proper step and overlap."""
    # Construct a string with predictable length: 250 characters
    text = "A" * 100 + "B" * 100 + "C" * 50
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    chunks = chunker.chunk_text(text=text, page_number=2, source_filename="long.pdf")

    # Step is chunk_size - chunk_overlap = 80
    # Chunk 0: index 0 to 100 (len 100)
    # Chunk 1: index 80 to 180 (len 100)
    # Chunk 2: index 160 to 250 (len 90)
    # Chunk 3: index 240 to 250 (len 10) or merged if minimal? Let's check step: 0, 80, 160, 240
    assert len(chunks) == 4
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 2
    assert chunks[0].source_filename == "long.pdf"
    assert chunks[0].text == text[0:100]

    assert chunks[1].chunk_index == 1
    assert chunks[1].text == text[80:180]
    # Check overlap: end of chunk 0 matches start of chunk 1
    assert chunks[0].text[80:100] == chunks[1].text[0:20]


def test_chunk_overlap_invalid_parameters():
    """Chunker should raise ValueError when chunk_overlap >= chunk_size or chunk_size <= 0."""
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        TextChunker(chunk_size=0, chunk_overlap=0)

    with pytest.raises(ValueError, match="chunk_overlap must be non-negative"):
        TextChunker(chunk_size=100, chunk_overlap=-5)

    with pytest.raises(ValueError, match="chunk_overlap must be strictly less than chunk_size"):
        TextChunker(chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError, match="chunk_overlap must be strictly less than chunk_size"):
        TextChunker(chunk_size=100, chunk_overlap=120)


def test_chunk_pages_preserves_page_boundaries_and_metadata():
    """Chunking multiple pages should respect page boundaries and assign continuous indices."""
    pages = [
        ExtractedPage(page_number=1, text="Page one text content.", char_count=23),
        ExtractedPage(page_number=2, text="Page two has different text content.", char_count=37),
    ]
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)

    chunks = chunker.chunk_pages(pages=pages, source_filename="report.pdf")

    assert len(chunks) == 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].source_filename == "report.pdf"
    assert chunks[0].text == "Page one text content."

    assert chunks[1].chunk_index == 1
    assert chunks[1].page_number == 2
    assert chunks[1].source_filename == "report.pdf"
    assert chunks[1].text == "Page two has different text content."


def test_chunk_multi_page_with_multiple_chunks_per_page():
    """Multi-page document where each page spans multiple chunks preserves correct page numbering."""
    p1_text = "Page 1 " * 40  # ~280 chars
    p2_text = "Page 2 " * 30  # ~210 chars
    pages = [
        ExtractedPage(page_number=1, text=p1_text.strip(), char_count=len(p1_text.strip())),
        ExtractedPage(page_number=2, text=p2_text.strip(), char_count=len(p2_text.strip())),
    ]
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    chunks = chunker.chunk_pages(pages=pages, source_filename="multi_page.pdf")

    assert len(chunks) > 2
    # Ensure sequential indices
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx
        assert c.source_filename == "multi_page.pdf"
        if "Page 1" in c.text:
            assert c.page_number == 1
        elif "Page 2" in c.text:
            assert c.page_number == 2
