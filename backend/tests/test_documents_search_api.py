"""Integration tests for document semantic search API endpoint."""

import io
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


def test_search_endpoint_with_uploaded_document(client: TestClient):
    """Test uploading a document and semantically querying it via POST /documents/search."""
    content = "PyTorch and Sentence Transformers enable dense semantic representations."
    pdf_bytes = create_in_memory_pdf([content])
    files = {"file": ("nlp_paper.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    upload_resp = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)
    assert upload_resp.status_code == 200
    doc_id = upload_resp.json()["document_id"]
    assert doc_id is not None

    # Search for related query
    search_payload = {
        "query": content,
        "top_k": 3,
    }
    search_resp = client.post(f"{settings.API_V1_STR}/documents/search", json=search_payload)
    assert search_resp.status_code == 200
    search_data = search_resp.json()

    assert search_data["query"] == content
    assert search_data["total_results"] >= 1
    top_match = search_data["results"][0]
    assert top_match["document_id"] == doc_id
    assert top_match["source_filename"] == "nlp_paper.pdf"
    assert top_match["page_number"] == 1
    assert "Sentence Transformers" in top_match["text"]
    assert isinstance(top_match["distance"], float)


def test_search_with_document_id_filter(client: TestClient):
    """Test restricting search to a specific document_id."""
    pdf_1 = create_in_memory_pdf(["Apple biology and fruit agriculture."])
    pdf_2 = create_in_memory_pdf(["Orange cultivation and citrus orchards."])

    resp_1 = client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("apples.pdf", io.BytesIO(pdf_1), "application/pdf")})
    resp_2 = client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("oranges.pdf", io.BytesIO(pdf_2), "application/pdf")})

    doc_id_1 = resp_1.json()["document_id"]
    doc_id_2 = resp_2.json()["document_id"]

    # Search filtered to doc_id_1
    search_resp = client.post(
        f"{settings.API_V1_STR}/documents/search",
        json={"query": "fruit agriculture", "top_k": 5, "document_id": doc_id_1},
    )
    assert search_resp.status_code == 200
    results = search_resp.json()["results"]
    for res in results:
        assert res["document_id"] == doc_id_1

    # Search filtered to doc_id_2
    search_resp_2 = client.post(
        f"{settings.API_V1_STR}/documents/search",
        json={"query": "fruit agriculture", "top_k": 5, "document_id": doc_id_2},
    )
    assert search_resp_2.status_code == 200
    results_2 = search_resp_2.json()["results"]
    for res in results_2:
        assert res["document_id"] == doc_id_2


def test_search_empty_query_rejected(client: TestClient):
    """Test that empty queries return 400 or 422 error."""
    resp = client.post(
        f"{settings.API_V1_STR}/documents/search",
        json={"query": "   ", "top_k": 5},
    )
    assert resp.status_code in (400, 422)


def test_search_invalid_top_k_rejected(client: TestClient):
    """Test that non-positive top_k returns 400 or 422 error."""
    resp = client.post(
        f"{settings.API_V1_STR}/documents/search",
        json={"query": "Valid query", "top_k": 0},
    )
    assert resp.status_code in (400, 422)


def test_delete_document_endpoint(client: TestClient):
    """Test deleting an uploaded document removes it from future searches."""
    pdf_bytes = create_in_memory_pdf(["Temporary document to be deleted."])
    upload_resp = client.post(
        f"{settings.API_V1_STR}/documents/upload",
        files={"file": ("to_delete.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    doc_id = upload_resp.json()["document_id"]

    # Delete the document
    del_resp = client.delete(f"{settings.API_V1_STR}/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"
    assert del_resp.json()["deleted_chunks"] >= 1

    # Search should now find 0 results for this document
    search_resp = client.post(
        f"{settings.API_V1_STR}/documents/search",
        json={"query": "Temporary document to be deleted.", "top_k": 5, "document_id": doc_id},
    )
    assert search_resp.status_code == 200
    assert search_resp.json()["total_results"] == 0
