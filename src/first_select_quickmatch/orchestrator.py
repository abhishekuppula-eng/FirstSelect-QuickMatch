from __future__ import annotations

from typing import Any

from first_select_quickmatch.agents.matching_agent import SupplierMatchingAgent
from first_select_quickmatch.agents.requirement_agent import RequirementFinalizationAgent
from first_select_quickmatch.agents.retrieval_agent import SearchRetrievalAgent
from first_select_quickmatch.agents.timekeeper_agent import TimekeeperAgent
from first_select_quickmatch.core.models import AgentResult, ChatMessage
from first_select_quickmatch.core.rules import build_conversation_state, extract_requirement_hints


class FourAgentOrchestrator:
    """4 agents:
    1) RequirementFinalizationAgent
    2) TimekeeperAgent
    3) SearchRetrievalAgent
    4) SupplierMatchingAgent
    """

    def __init__(
        self,
        requirement_agent: RequirementFinalizationAgent,
        matching_agent: SupplierMatchingAgent,
        retrieval_agent: SearchRetrievalAgent | None = None,
        timekeeper_agent: TimekeeperAgent | None = None,
    ):
        self.requirement_agent = requirement_agent
        self.matching_agent = matching_agent
        self.retrieval_agent = retrieval_agent or SearchRetrievalAgent()
        self.timekeeper_agent = timekeeper_agent or TimekeeperAgent()

    def run(
        self,
        messages: list[dict[str, str]],
        facilities: list[dict[str, Any]],
        elapsed_minutes: float = 0.0,
    ) -> AgentResult:
        parsed = [ChatMessage(**m) for m in messages]
        state = build_conversation_state(parsed, elapsed_minutes=elapsed_minutes)

        if not state.is_confirmed:
            if self.timekeeper_agent.should_force_summarize(state):
                state.timekeeper_triggered = True
            return self.requirement_agent.run(parsed, state)

        hints = extract_requirement_hints(parsed)
        pre_scored = self.retrieval_agent.run(facilities, hints)
        result = self.matching_agent.run(hints, pre_scored)
        result.metadata = {
            "matched_count": len(pre_scored),
            "is_confirmed": state.is_confirmed,
        }
        return result
