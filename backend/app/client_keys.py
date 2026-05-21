"""Ephemeral API keys sent from the browser — used once per request, never stored."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

LlmProvider = Literal["openai", "anthropic", "google"]


class ClientApiKeys(BaseModel):
    """Keys live only in this request body; the server does not write them to disk."""

    llm_provider: Optional[LlmProvider] = None
    llm_api_key: Optional[str] = Field(default=None, max_length=512)
    llm_model: Optional[str] = Field(default=None, max_length=128)
    tavily_api_key: Optional[str] = Field(default=None, max_length=512)

    def llm_configured(self) -> bool:
        return bool(self.llm_provider and self.llm_api_key and self.llm_api_key.strip())

    def tavily_configured(self) -> bool:
        return bool(self.tavily_api_key and self.tavily_api_key.strip())
