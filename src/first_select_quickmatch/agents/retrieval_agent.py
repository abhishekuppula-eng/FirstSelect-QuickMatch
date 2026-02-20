from __future__ import annotations

from typing import Any

from first_select_quickmatch.core.models import FacilityMatch, RequirementHints
from first_select_quickmatch.db.matching import search_suppliers


class SearchRetrievalAgent:
    def run(self, facilities: list[dict[str, Any]], hints: RequirementHints) -> list[FacilityMatch]:
        return search_suppliers(facilities, hints)
