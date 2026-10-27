"""Unit tests for the modular RAG service."""

import pytest
from app.schemas.chat import ChatResponse
from app.schemas.documents import SearchResult
from app.services.rag_service import RAGService


class MockVectorStore:
    def __init__(self, passages: list[SearchResult] | None = None):
        self.passages = passages if passages is not None else []
        self.last_query = None
        self.last_top_k = None
        self.last_doc_id = None

    def search(self, query: str, top_k: int = 5, document_id: str | None = None) -> list[SearchResult]:
        self.last_query = query
        self.last_top_k = top_k
        self.last_doc_id = document_id
        return self.passages


class MockLLMClient:
    def __init__(self, answer: str = "Default answer [Source: doc.pdf, Page 1]"):
        self.answer = answer
        self.model = "mock-llama3.2"
        self.call_count = 0
        self.last_messages = None

    def generate(self, messages: list[dict[str, str]], temperature: float | None = None) -> str:
        self.call_count += 1
        self.last_messages = messages
        return self.answer


def test_rag_service_with_sufficient_evidence():
    """Test standard flow when relevant passages are retrieved and model answers with citations."""
    sample_passages = [
        SearchResult(
            text="ResearchPilot supports semantic vector search using ChromaDB.",
            source_filename="pilot_overview.pdf",
            page_number=1,
            chunk_index=0,
            document_id="doc-99",
            distance=0.12,
            metadata={},
        ),
        SearchResult(
            text="Documents are chunked with configurable overlap.",
            source_filename="pilot_overview.pdf",
            page_number=2,
            chunk_index=1,
            document_id="doc-99",
            distance=0.25,
            metadata={},
        ),
    ]

    vector_store = MockVectorStore(passages=sample_passages)
    llm_client = MockLLMClient(
        answer="ResearchPilot utilizes ChromaDB for semantic search [Source: pilot_overview.pdf, Page 1]."
    )
    rag_service = RAGService(vector_store=vector_store, llm_client=llm_client)

    response = rag_service.answer_question("How does semantic search work in ResearchPilot?")

    assert isinstance(response, ChatResponse)
    assert response.has_sufficient_evidence is True
    assert "ChromaDB" in response.answer
    assert len(response.evidence) == 2
    assert response.evidence[0].source_filename == "pilot_overview.pdf"
    assert response.evidence[0].page_number == 1
    assert len(response.citations) >= 1
    assert response.citations[0].source_filename == "pilot_overview.pdf"
    assert response.citations[0].page_number == 1
    assert llm_client.call_count == 1


def test_rag_service_with_no_retrieved_evidence():
    """When vector search returns empty results, service reports insufficient evidence without calling LLM."""
    vector_store = MockVectorStore(passages=[])
    llm_client = MockLLMClient()
    rag_service = RAGService(vector_store=vector_store, llm_client=llm_client)

    response = rag_service.answer_question("What is the capital of Mars?")

    assert response.has_sufficient_evidence is False
    assert "insufficient evidence" in response.answer.lower()
    assert response.citations == []
    assert response.evidence == []
    assert llm_client.call_count == 0  # LLM should not be called unnecessarily


def test_rag_service_model_admits_insufficient_evidence():
    """When LLM admits passages do not contain evidence, has_sufficient_evidence is False."""
    sample_passages = [
        SearchResult(
            text="The sky is blue due to Rayleigh scattering.",
            source_filename="physics.pdf",
            page_number=4,
            chunk_index=0,
            document_id="doc-44",
            distance=0.45,
            metadata={},
        )
    ]
    vector_store = MockVectorStore(passages=sample_passages)
    llm_client = MockLLMClient(
        answer="I cannot answer this question based on the provided documents as there is insufficient evidence."
    )
    rag_service = RAGService(vector_store=vector_store, llm_client=llm_client)

    response = rag_service.answer_question("What was Napoleon's favorite food?")

    assert response.has_sufficient_evidence is False
    assert "insufficient evidence" in response.answer.lower()
    assert response.citations == []
    assert len(response.evidence) == 1


def test_rag_service_validates_question_input():
    """Verify empty questions and questions exceeding max length raise ValueError."""
    vector_store = MockVectorStore(passages=[])
    llm_client = MockLLMClient()
    rag_service = RAGService(vector_store=vector_store, llm_client=llm_client)

    with pytest.raises(ValueError, match="Question cannot be empty"):
        rag_service.answer_question("")

    with pytest.raises(ValueError, match="Question cannot be empty"):
        rag_service.answer_question("   \n\t  ")

    with pytest.raises(ValueError, match="Question exceeds maximum allowed length"):
        rag_service.answer_question("x" * 1001)
