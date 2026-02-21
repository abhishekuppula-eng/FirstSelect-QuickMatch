from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    def complete(self, system: str, messages: list[dict[str, str]]) -> str: ...


@dataclass
class StaticLLMClient:
    """Fallback test client for deterministic local behavior."""

    static_text: str = ""

    def complete(self, system: str, messages: list[dict[str, str]]) -> str:
        _ = system, messages
        return self.static_text
