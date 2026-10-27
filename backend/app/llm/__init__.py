"""LLM integration module: provider interfaces, prompts, and local model adapters."""

from app.llm.exceptions import (
    LLMError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)
from app.llm.ollama_client import OllamaClient
from app.llm.prompts import SYSTEM_PROMPT, build_rag_messages

__all__ = [
    "OllamaClient",
    "SYSTEM_PROMPT",
    "build_rag_messages",
    "LLMError",
    "OllamaConnectionError",
    "OllamaModelNotFoundError",
    "OllamaTimeoutError",
    "OllamaResponseError",
]

