"""Automated integration tests for document upload API."""

import io
import pytest
from fastapi.testclient import TestClient
import pymupdf

from app.core.config import settings


def create_in_memory_pdf(pages: list[str]) -> bytes:
    """Create in-memory PDF bytes with text on each page."""
    doc = pymupdf.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_encrypted_pdf(text: str = "Confidential", password: str = "password123") -> bytes:
    """Create encrypted PDF bytes."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    doc.save(
        "temp_enc_api.pdf",
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw=password,
        user_pw=password,
    )
    doc.close()
    with open("temp_enc_api.pdf", "rb") as f:
        data = f.read()
    import os
    os.remove("temp_enc_api.pdf")
    return data


def test_upload_valid_single_page_pdf(client: TestClient):
    """Test uploading a valid single-page PDF to /api/v1/documents/upload."""
    pdf_bytes = create_in_memory_pdf(["ResearchPilot AI document ingestion test."])
    files = {"file": ("sample.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample.pdf"
    assert data["page_count"] == 1
    assert data["file_size_bytes"] == len(pdf_bytes)
    assert data["total_chunks"] >= 1
    assert len(data["pages"]) == 1
    assert data["pages"][0]["page_number"] == 1
    assert "ResearchPilot AI" in data["pages"][0]["text"]
    assert data["chunks"][0]["page_number"] == 1
    assert data["chunks"][0]["source_filename"] == "sample.pdf"


def test_upload_root_documents_endpoint(client: TestClient):
    """Test POST /documents/upload works directly according to spec."""
    pdf_bytes = create_in_memory_pdf(["Testing root /documents/upload route."])
    files = {"file": ("root_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    response = client.post("/documents/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "root_test.pdf"
    assert data["page_count"] == 1


def test_upload_valid_multipage_pdf(client: TestClient):
    """Test uploading a multi-page PDF."""
    pdf_bytes = create_in_memory_pdf([
        "Introduction to document research.",
        "Methodology and vector search strategies.",
        "Evaluation metrics and conclusion.",
    ])
    files = {"file": ("paper.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "paper.pdf"
    assert data["page_count"] == 3
    assert len(data["pages"]) == 3
    assert data["pages"][0]["page_number"] == 1
    assert data["pages"][1]["page_number"] == 2
    assert data["pages"][2]["page_number"] == 3
    assert data["total_chunks"] >= 3


def test_upload_non_pdf_file_rejected(client: TestClient):
    """Test that non-PDF files are rejected with 400 Bad Request."""
    files = {"file": ("notes.txt", io.BytesIO(b"Just some plain text notes."), "text/plain")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_upload_empty_file_rejected(client: TestClient):
    """Test that zero-byte files are rejected with 400 Bad Request."""
    files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_upload_corrupted_file_rejected(client: TestClient):
    """Test that corrupted files are rejected with 400 Bad Request."""
    files = {"file": ("corrupt.pdf", io.BytesIO(b"%PDF-1.4 corrupted binary trash"), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 400
    assert "not a valid or readable PDF" in response.json()["detail"]


def test_upload_encrypted_file_rejected(client: TestClient):
    """Test that encrypted/password-protected PDFs are rejected with 400 Bad Request."""
    encrypted_bytes = create_encrypted_pdf("Secret text")
    files = {"file": ("locked.pdf", io.BytesIO(encrypted_bytes), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 400
    assert "Password-protected or encrypted" in response.json()["detail"]


def test_upload_pdf_with_no_text_rejected(client: TestClient):
    """Test that PDFs without any extractable text (e.g. blank/scanned) return 422 Unprocessable Entity."""
    blank_pdf = create_in_memory_pdf(["", ""])
    files = {"file": ("scanned.pdf", io.BytesIO(blank_pdf), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 422
    assert "OCR" in response.json()["detail"]


def test_upload_file_size_exceeded(client: TestClient, monkeypatch):
    """Test that uploading a file larger than MAX_UPLOAD_SIZE_BYTES returns 413 Payload Too Large."""
    # Set a tiny max size of 50 bytes for this test
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 50)
    pdf_bytes = create_in_memory_pdf(["Text that exceeds fifty bytes in total size."])
    files = {"file": ("large.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    response = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)

    assert response.status_code == 413
    assert "exceeds the maximum" in response.json()["detail"]


def test_health_endpoints_still_pass(client: TestClient):
    """Verify that health check endpoints remain completely intact."""
    root_health = client.get("/health")
    assert root_health.status_code == 200
    assert root_health.json()["status"] == "ok"

    v1_health = client.get(f"{settings.API_V1_STR}/health")
    assert v1_health.status_code == 200
    assert v1_health.json()["status"] == "ok"
