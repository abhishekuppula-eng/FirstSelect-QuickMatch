from first_select_quickmatch.agents.retrieval_agent import SearchRetrievalAgent
from first_select_quickmatch.core.models import RequirementHints


class FakePostgresMCP:
    def __init__(self, rows):
        self.rows = rows
        self.last_query = None
        self.last_params = None

    def run_sql(self, query, params):
        self.last_query = query
        self.last_params = params
        return self.rows


def test_build_query_contains_expected_filters():
    agent = SearchRetrievalAgent()
    hints = RequirementHints(
        service_type="warehouse",
        location="texas",
        integration_methods=["api", "edi"],
        is_food_grade=True,
        order_volume=5000,
    )
    q = agent.build_query(hints, limit=25)
    assert "FROM public.facilities" in q.sql
    assert "f.integration_methods && %s::text[]" in q.sql
    assert "LOWER(f.location) LIKE %s" in q.sql
    assert q.params[-1] == 25


def test_retrieval_prefers_mcp_rows_over_fallback_facilities():
    mcp_rows = [
        {
            "id": "f1",
            "facility_name": "A",
            "location": "Texas",
            "service_type": "warehouse",
            "inbound_capabilities": ["pallet"],
            "outbound_capabilities": ["parcel"],
            "certifications": ["FDA"],
            "integration_methods": ["api"],
            "temperature_range_min": 35,
            "temperature_range_max": 45,
            "max_sqft": 40000,
            "max_order_volume": 10000,
            "suppliers": {"name": "Company A", "star_rating": 4.8, "verified": True, "total_reviews": 12},
        }
    ]
    fake = FakePostgresMCP(mcp_rows)
    agent = SearchRetrievalAgent(postgres_client=fake)

    hints = RequirementHints(location="texas", service_type="warehouse", temperature_preferred=True)
    matches = agent.run(facilities=[], hints=hints)

    assert fake.last_query is not None
    assert matches
    assert matches[0].facility_name == "A"
