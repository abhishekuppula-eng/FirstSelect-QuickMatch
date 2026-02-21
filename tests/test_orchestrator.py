from first_select_quickmatch.agents.base import StaticLLMClient
from first_select_quickmatch.agents.matching_agent import SupplierMatchingAgent
from first_select_quickmatch.agents.requirement_agent import RequirementFinalizationAgent
from first_select_quickmatch.orchestrator import FourAgentOrchestrator


def _orchestrator(req_text: str = "need more info", match_text: str = "ranked summary"):
    return FourAgentOrchestrator(
        requirement_agent=RequirementFinalizationAgent(StaticLLMClient(req_text)),
        matching_agent=SupplierMatchingAgent(StaticLLMClient(match_text)),
    )


def test_orchestrator_routes_to_requirement_mode_when_not_confirmed():
    orch = _orchestrator(req_text="please share more details")
    out = orch.run(
        messages=[{"role": "user", "content": "Need warehousing"}],
        facilities=[],
        elapsed_minutes=1.0,
    )
    assert out.mode == "requirement"
    assert "share" in out.response_text


def test_orchestrator_routes_to_matching_mode_when_confirmed():
    orch = _orchestrator(match_text="Top options appear aligned based on available data.")
    facilities = [
        {
            "id": "f1",
            "facility_name": "A",
            "location": "Texas",
            "inbound_capabilities": ["pallet"],
            "outbound_capabilities": ["parcel"],
            "certifications": ["FDA"],
            "is_food_grade": True,
            "integration_methods": ["api"],
            "temperature_range_min": 35,
            "temperature_range_max": 45,
            "max_sqft": 50000,
            "max_order_volume": 10000,
            "suppliers": {"name": "Company A", "star_rating": 4.5, "verified": True, "total_reviews": 22},
        }
    ]
    out = orch.run(
        messages=[
            {"role": "assistant", "content": "Requirement summary - does this look right?"},
            {"role": "user", "content": "Yes proceed and find suppliers"},
            {"role": "user", "content": "Need cold storage warehouse in Texas with api 5000 orders per month"},
            {"role": "assistant", "content": "Requirement summary confirmed. Ready to search?"},
            {"role": "user", "content": "search now"},
        ],
        facilities=facilities,
        elapsed_minutes=4.0,
    )
    assert out.mode == "matching"
    assert out.tool_payload is not None
    assert out.tool_payload["name"] == "present_matching_suppliers"
