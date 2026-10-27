"""Ollama HTTP API client provider for local LLM inference."""

import logging
from typing import Optional
import httpx

from app.core.config import settings
from app.llm.exceptions import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local inference via Ollama's HTTP API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout if timeout is not None else settings.OLLAMA_TIMEOUT_SECONDS
        self.http_client = http_client or httpx.Client(timeout=self.timeout)

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """Send chat messages to Ollama and return the generated completion string.

        Args:
            messages: List of chat messages (e.g. system, user).
            temperature: Sampling temperature for generation.

        Returns:
            The model's generated text response.

        Raises:
            OllamaConnectionError: If Ollama daemon is unreachable.
            OllamaTimeoutError: If the request times out.
            OllamaModelNotFoundError: If the configured model is not installed.
            OllamaResponseError: If Ollama returns an error status or malformed response.
        """
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
            },
        }

        try:
            response = self.http_client.post(url, json=payload, timeout=self.timeout)
        except httpx.ConnectError as e:
            logger.error("Failed to connect to Ollama at %s: %s", self.base_url, str(e))
            raise OllamaConnectionError(
                f"Ollama service is unreachable at '{self.base_url}'. Please ensure Ollama is installed and running."
            ) from e
        except httpx.TimeoutException as e:
            logger.error("Ollama request timed out after %s seconds: %s", self.timeout, str(e))
            raise OllamaTimeoutError(
                f"Ollama generation request timed out after {self.timeout} seconds."
            ) from e
        except Exception as e:
            logger.error("Unexpected error contacting Ollama: %s", str(e))
            raise OllamaResponseError(f"Error contacting Ollama: {e}") from e

        if response.status_code == 404:
            logger.error("Model '%s' not found on Ollama server (%s)", self.model, response.text)
            raise OllamaModelNotFoundError(
                f"Configured Ollama model '{self.model}' was not found. Download it using `ollama pull {self.model}`."
            )

        if response.is_error:
            logger.error("Ollama error response (status %s): %s", response.status_code, response.text)
            raise OllamaResponseError(
                f"Ollama request failed with status {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
            return data["message"]["content"]
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Malformed JSON received from Ollama: %s", response.text)
            raise OllamaResponseError(f"Malformed response payload received from Ollama: {e}") from e
