from __future__ import annotations

import os

from first_select_quickmatch.agents.base import LLMClient

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover
    Anthropic = None  # type: ignore


class AnthropicLLMClient(LLMClient):
    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic else None

    def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        if not self.client:
            return "[fallback] Claude client not configured."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            temperature=0,
            system=system,
            messages=messages,
        )
        return "\n".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
