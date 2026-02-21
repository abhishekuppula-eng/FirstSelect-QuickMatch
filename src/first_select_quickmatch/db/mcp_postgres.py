from __future__ import annotations

from typing import Any, Protocol


class PostgresMCPClient(Protocol):
    """Protocol for an MCP Postgres adapter.

    Expected minimal behavior:
    - run_sql(query: str, params: list[Any]) -> list[dict[str, Any]]
    """

    def run_sql(self, query: str, params: list[Any]) -> list[dict[str, Any]]: ...


class NoopPostgresMCPClient:
    """Fallback used when no PostgreSQL MCP integration is configured."""

    def run_sql(self, query: str, params: list[Any]) -> list[dict[str, Any]]:
        _ = query, params
        return []
