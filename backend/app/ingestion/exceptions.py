"""Custom exceptions for document ingestion and parsing."""


class IngestionError(Exception):
    """Base exception for all document ingestion errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EmptyPDFError(IngestionError):
    """Raised when the uploaded PDF file is 0 bytes or has no pages."""


class InvalidPDFError(IngestionError):
    """Raised when the uploaded file is corrupted or not a valid PDF."""


class EncryptedPDFError(IngestionError):
    """Raised when the uploaded PDF is password-protected or encrypted."""


class FileSizeExceededError(IngestionError):
    """Raised when the uploaded file exceeds the maximum allowed size."""


class NoExtractableTextError(IngestionError):
    """Raised when the PDF has pages but contains no extractable text (e.g. scanned image)."""
