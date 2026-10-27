"""Exceptions for LLM and Ollama provider integrations."""


class LLMError(Exception):
    """Base exception for all LLM provider errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OllamaConnectionError(LLMError):
    """Raised when the Ollama service cannot be reached."""


class OllamaModelNotFoundError(LLMError):
    """Raised when the requested model is not found on the Ollama server."""


class OllamaTimeoutError(LLMError):
    """Raised when an Ollama generation request times out."""


class OllamaResponseError(LLMError):
    """Raised when Ollama returns an error or malformed payload."""
