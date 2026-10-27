"""Modular PDF extraction service using PyMuPDF."""

import logging
from typing import Optional
import pymupdf

from app.core.config import settings
from app.ingestion.exceptions import (
    EmptyPDFError,
    EncryptedPDFError,
    FileSizeExceededError,
    InvalidPDFError,
    NoExtractableTextError,
)
from app.schemas.documents import ExtractedPage

logger = logging.getLogger(__name__)


class PDFParser:
    """Service to validate and extract page-aware text from PDF documents."""

    def __init__(self, max_file_size: Optional[int] = None) -> None:
        self.max_file_size = (
            max_file_size if max_file_size is not None else settings.MAX_UPLOAD_SIZE_BYTES
        )

    def normalize_text(self, text: str) -> str:
        """Conservatively clean extracted text without destroying paragraphs or tables.

        Removes null bytes and standardizes line endings while preserving layout structure.
        """
        if not text:
            return ""
        # Remove null bytes
        cleaned = text.replace("\x00", "")
        # Normalize carriage returns to standard newlines
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        # Strip outer whitespace
        return cleaned.strip()

    def extract_text(self, pdf_bytes: bytes, filename: str = "document.pdf") -> list[ExtractedPage]:
        """Validate and extract text page by page from raw PDF bytes.

        Args:
            pdf_bytes: Raw bytes of the uploaded PDF file.
            filename: Source filename for logging and error reporting.

        Returns:
            A list of ExtractedPage objects with 1-based page numbering.

        Raises:
            EmptyPDFError: If file is 0 bytes or has 0 pages.
            FileSizeExceededError: If file exceeds maximum allowed size.
            InvalidPDFError: If file is corrupted or not a valid PDF.
            EncryptedPDFError: If file is password-protected.
            NoExtractableTextError: If no extractable text is present on any page.
        """
        if not pdf_bytes:
            raise EmptyPDFError(f"The uploaded file '{filename}' is empty (0 bytes).")

        if len(pdf_bytes) > self.max_file_size:
            raise FileSizeExceededError(
                f"File '{filename}' size ({len(pdf_bytes)} bytes) exceeds the maximum allowed limit of {self.max_file_size} bytes."
            )

        doc = None
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.warning("Failed to open PDF '%s': %s", filename, str(e))
            raise InvalidPDFError(f"The uploaded file '{filename}' is not a valid or readable PDF.") from e

        try:
            if doc.is_encrypted or doc.needs_pass:
                raise EncryptedPDFError(
                    f"Password-protected or encrypted PDFs are not supported: '{filename}'."
                )

            if doc.page_count == 0:
                raise EmptyPDFError(f"The PDF document '{filename}' contains no pages.")

            extracted_pages: list[ExtractedPage] = []
            total_text_length = 0

            for page_index in range(doc.page_count):
                page = doc[page_index]
                raw_text = page.get_text("text")
                normalized_text = self.normalize_text(raw_text)
                char_count = len(normalized_text)
                total_text_length += char_count

                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_index + 1,  # 1-based page number
                        text=normalized_text,
                        char_count=char_count,
                    )
                )

            if total_text_length == 0:
                raise NoExtractableTextError(
                    f"The PDF '{filename}' contains no extractable text. Scanned or image-only PDFs require OCR, which is not supported."
                )

            return extracted_pages
        finally:
            if doc is not None:
                doc.close()
