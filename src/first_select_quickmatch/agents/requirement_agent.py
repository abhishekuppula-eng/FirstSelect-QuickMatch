from __future__ import annotations

from first_select_quickmatch.agents.base import LLMClient
from first_select_quickmatch.core.models import AgentResult, ChatMessage, ConversationState
from first_select_quickmatch.core.prompts import GLOBAL_SYSTEM_RULES, REQUIREMENT_AGENT_PROMPT, TIMEKEEPER_FORCE_SUMMARIZE


class RequirementFinalizationAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, messages: list[ChatMessage], state: ConversationState) -> AgentResult:
        system = f"{GLOBAL_SYSTEM_RULES}\n\n{REQUIREMENT_AGENT_PROMPT}"
        if state.timekeeper_triggered:
            system += f"\n\n{TIMEKEEPER_FORCE_SUMMARIZE}"

        system += (
            "\n\nCONVERSATION STATE:\n"
            f"- Questions asked so far: {state.question_count}\n"
            f"- Elapsed time: {state.elapsed_minutes:.1f} minutes\n"
            f"- Remaining question budget: {max(0, 8 - state.question_count)}"
        )

        content = self.llm.complete(system, [m.__dict__ for m in messages])
        return AgentResult(mode="requirement", response_text=content, metadata={"timekeeper": state.timekeeper_triggered})
