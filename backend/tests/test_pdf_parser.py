"""Unit tests for PDF extraction and parsing."""

import pytest
import pymupdf

from app.ingestion.exceptions import (
    EmptyPDFError,
    EncryptedPDFError,
    FileSizeExceededError,
    InvalidPDFError,
    NoExtractableTextError,
)
from app.ingestion.pdf_parser import PDFParser


def create_test_pdf(pages_text: list[str]) -> bytes:
    """Helper to create an in-memory PDF with specified text per page."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        if text:
            page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_encrypted_test_pdf(text: str, password: str = "secret") -> bytes:
    """Helper to create an encrypted in-memory PDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    # PyMuPDF encryption
    perm = int(
        pymupdf.PDF_PERM_ACCESSIBILITY
        | pymupdf.PDF_PERM_PRINT
        | pymupdf.PDF_PERM_COPY
        | pymupdf.PDF_PERM_ANNOTATE
    )
    doc.save(
        "temp_encrypted.pdf",
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw=password,
        user_pw=password,
        permissions=perm,
    )
    doc.close()
    with open("temp_encrypted.pdf", "rb") as f:
        pdf_bytes = f.read()
    import os
    os.remove("temp_encrypted.pdf")
    return pdf_bytes


def test_extract_single_page_pdf():
    """Test extracting text from a single page valid PDF."""
    content = "Hello ResearchPilot AI, this is page 1."
    pdf_bytes = create_test_pdf([content])
    parser = PDFParser()

    pages = parser.extract_text(pdf_bytes, filename="test_single.pdf")

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert content in pages[0].text
    assert pages[0].char_count == len(pages[0].text)


def test_extract_multi_page_pdf():
    """Test extracting text from a multi-page valid PDF with 1-based page numbering."""
    p1 = "First page research evidence."
    p2 = "Second page methodology details."
    p3 = "Third page conclusion findings."
    pdf_bytes = create_test_pdf([p1, p2, p3])
    parser = PDFParser()

    pages = parser.extract_text(pdf_bytes, filename="multipage.pdf")

    assert len(pages) == 3
    assert pages[0].page_number == 1
    assert p1 in pages[0].text
    assert pages[1].page_number == 2
    assert p2 in pages[1].text
    assert pages[2].page_number == 3
    assert p3 in pages[2].text


def test_empty_pdf_bytes_raises_empty_error():
    """Test that zero-byte input raises EmptyPDFError."""
    parser = PDFParser()
    with pytest.raises(EmptyPDFError, match="empty"):
        parser.extract_text(b"", filename="empty.pdf")


def test_corrupted_pdf_bytes_raises_invalid_error():
    """Test that corrupted non-PDF bytes raise InvalidPDFError."""
    parser = PDFParser()
    with pytest.raises(InvalidPDFError, match="not a valid"):
        parser.extract_text(b"This is not a PDF file content", filename="corrupt.pdf")


def test_password_protected_pdf_raises_encrypted_error():
    """Test that encrypted/password-protected PDFs raise EncryptedPDFError."""
    encrypted_bytes = create_encrypted_test_pdf("Secret content")
    parser = PDFParser()
    with pytest.raises(EncryptedPDFError, match="Password-protected or encrypted"):
        parser.extract_text(encrypted_bytes, filename="encrypted.pdf")


def test_pdf_with_no_extractable_text_raises_error():
    """Test that PDF with empty pages and no extractable text raises NoExtractableTextError."""
    # Blank pages without text
    pdf_bytes = create_test_pdf(["", ""])
    parser = PDFParser()
    with pytest.raises(NoExtractableTextError, match="no extractable text"):
        parser.extract_text(pdf_bytes, filename="blank.pdf")


def test_file_size_exceeded_raises_error():
    """Test that exceeding the max_file_size limit raises FileSizeExceededError."""
    pdf_bytes = create_test_pdf(["Some text"])
    parser = PDFParser(max_file_size=len(pdf_bytes) - 1)
    with pytest.raises(FileSizeExceededError, match="exceeds the maximum"):
        parser.extract_text(pdf_bytes, filename="large.pdf")
