"""RAG question-answering coordination service."""

import logging
import re
from typing import Optional

from app.core.config import settings
from app.llm.ollama_client import OllamaClient
from app.llm.prompts import build_rag_messages
from app.retrieval.vector_store import VectorStore
from app.schemas.chat import ChatResponse, Citation, EvidencePassage

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_PHRASE = (
    "I cannot answer this question based on the provided documents as there is insufficient evidence."
)


class RAGService:
    """Service orchestrating semantic retrieval, grounded prompt construction, and Ollama answer generation."""

    def __init__(
        self,
        vector_store: VectorStore,
        llm_client: OllamaClient,
    ) -> None:
        self.vector_store = vector_store
        self.llm_client = llm_client

    def _extract_citations(self, answer: str, passages: list) -> list[Citation]:
        """Extract validated citations from model answer mapped strictly to retrieved passages."""
        # Find citations in format [Source: <filename>, Page <page_number>]
        pattern = re.compile(r"\[Source:\s*([^,]+),\s*Page\s*(\d+)\]", re.IGNORECASE)
        matches = pattern.findall(answer)

        passage_lookup = {
            (p.source_filename.strip().lower(), p.page_number): p for p in passages
        }

        matched_citations: list[Citation] = []
        seen = set()

        for filename, page_str in matches:
            fname = filename.strip().lower()
            p_num = int(page_str)
            key = (fname, p_num)

            # Match against actual retrieved passages (no fabricated citations)
            if key in passage_lookup and key not in seen:
                seen.add(key)
                passage = passage_lookup[key]
                matched_citations.append(
                    Citation(
                        source_filename=passage.source_filename,
                        page_number=passage.page_number,
                        document_id=passage.document_id,
                        chunk_index=passage.chunk_index,
                    )
                )

        # Fallback: if model answered from evidence without explicit brackets, cite the retrieved passages
        if not matched_citations and passages:
            for p in passages:
                key = (p.source_filename.strip().lower(), p.page_number)
                if key not in seen:
                    seen.add(key)
                    matched_citations.append(
                        Citation(
                            source_filename=p.source_filename,
                            page_number=p.page_number,
                            document_id=p.document_id,
                            chunk_index=p.chunk_index,
                        )
                    )

        return matched_citations

    def answer_question(
        self,
        question: str,
        document_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> ChatResponse:
        """Process a question using RAG: retrieve passages, build grounded prompt, generate answer with citations.

        Args:
            question: User question string.
            document_id: Optional document ID to filter search scope.
            top_k: Number of chunks to retrieve.

        Returns:
            ChatResponse with answer, citations, and evidence passages.

        Raises:
            ValueError: If question is empty or exceeds maximum length.
        """
        cleaned_question = question.strip() if question else ""
        if not cleaned_question:
            raise ValueError("Question cannot be empty.")

        if len(cleaned_question) > settings.MAX_QUESTION_LENGTH:
            raise ValueError(
                f"Question exceeds maximum allowed length of {settings.MAX_QUESTION_LENGTH} characters."
            )

        k = top_k if top_k is not None else settings.DEFAULT_TOP_K

        # Step 1: Semantic retrieval
        passages = self.vector_store.search(
            query=cleaned_question,
            top_k=k,
            document_id=document_id,
        )

        # Step 2: Handle empty retrieval immediately without calling LLM
        if not passages:
            return ChatResponse(
                question=cleaned_question,
                answer=INSUFFICIENT_EVIDENCE_PHRASE,
                citations=[],
                evidence=[],
                has_sufficient_evidence=False,
                model=self.llm_client.model,
            )

        # Step 3: Format evidence passages
        evidence_passages = [
            EvidencePassage(
                text=p.text,
                source_filename=p.source_filename,
                page_number=p.page_number,
                document_id=p.document_id,
                chunk_index=p.chunk_index,
                distance=p.distance,
            )
            for p in passages
        ]

        # Step 4: Build grounded prompt
        messages = build_rag_messages(question=cleaned_question, passages=passages)

        # Step 5: Generate answer with Ollama
        generated_answer = self.llm_client.generate(messages=messages)

        # Step 6: Determine groundedness and citations
        if "insufficient evidence" in generated_answer.lower():
            has_sufficient_evidence = False
            citations = []
        else:
            has_sufficient_evidence = True
            citations = self._extract_citations(answer=generated_answer, passages=passages)

        return ChatResponse(
            question=cleaned_question,
            answer=generated_answer,
            citations=citations,
            evidence=evidence_passages,
            has_sufficient_evidence=has_sufficient_evidence,
            model=self.llm_client.model,
        )
