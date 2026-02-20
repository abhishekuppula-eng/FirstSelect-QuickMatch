from __future__ import annotations

from typing import Any

from first_select_quickmatch.core.models import FacilityMatch, RequirementHints
from first_select_quickmatch.db.matching import search_suppliers
from first_select_quickmatch.db.mcp_postgres import NoopPostgresMCPClient, PostgresMCPClient
from first_select_quickmatch.db.sql_builder import PostgresQueryBuilder, SQLQuery


class SearchRetrievalAgent:
    """Retrieval agent with dual mode:
    1) MCP Postgres (preferred): build SQL from hints and execute via MCP adapter.
    2) In-memory fallback: use provided facilities list.
    """

    def __init__(
        self,
        postgres_client: PostgresMCPClient | None = None,
        query_builder: PostgresQueryBuilder | None = None,
    ):
        self.postgres_client = postgres_client or NoopPostgresMCPClient()
        self.query_builder = query_builder or PostgresQueryBuilder()

    def build_query(self, hints: RequirementHints, limit: int = 200) -> SQLQuery:
        return self.query_builder.build(hints, limit=limit)

    def run(self, facilities: list[dict[str, Any]], hints: RequirementHints) -> list[FacilityMatch]:
        query = self.build_query(hints)
        rows = self.postgres_client.run_sql(query.sql, query.params)
        candidates = rows if rows else facilities
        return search_suppliers(candidates, hints)
