"""Backward-compatible entrypoint for the packaged 4-agent system."""

from first_select_quickmatch.agents.base import StaticLLMClient
from first_select_quickmatch.agents.matching_agent import SupplierMatchingAgent
from first_select_quickmatch.agents.requirement_agent import RequirementFinalizationAgent
from first_select_quickmatch.orchestrator import FourAgentOrchestrator


if __name__ == "__main__":
    orchestrator = FourAgentOrchestrator(
        requirement_agent=RequirementFinalizationAgent(StaticLLMClient("Please share your product type and monthly volume.")),
        matching_agent=SupplierMatchingAgent(StaticLLMClient("Top options appear aligned based on available data.")),
    )

    demo_messages = [{"role": "user", "content": "We need cold storage in Texas for 4,000 orders per month."}]
    demo_facilities = []
    result = orchestrator.run(demo_messages, demo_facilities, elapsed_minutes=1.2)
    print(result)
