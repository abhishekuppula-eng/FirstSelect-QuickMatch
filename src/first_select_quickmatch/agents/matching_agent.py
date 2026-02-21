from __future__ import annotations

from first_select_quickmatch.agents.base import LLMClient
from first_select_quickmatch.core.models import AgentResult, FacilityMatch, RequirementHints
from first_select_quickmatch.core.prompts import GLOBAL_SYSTEM_RULES, MATCHING_AGENT_PROMPT


class SupplierMatchingAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, hints: RequirementHints, pre_scored: list[FacilityMatch]) -> AgentResult:
        top = pre_scored[:5]
        system = f"{GLOBAL_SYSTEM_RULES}\n\n{MATCHING_AGENT_PROMPT}"
        user_prompt = (
            "CONFIRMED BUYER REQUIREMENTS:\n"
            f"{hints.__dict__}\n\n"
            f"PRE-SCORED SUPPLIERS ({len(pre_scored)}):\n"
            f"{[m.__dict__ for m in top]}"
        )
        summary = self.llm.complete(system, [{"role": "user", "content": user_prompt}])
        return AgentResult(
            mode="matching",
            response_text=summary,
            tool_payload={"name": "present_matching_suppliers", "input": {"suppliers": [m.__dict__ for m in top]}},
        )
