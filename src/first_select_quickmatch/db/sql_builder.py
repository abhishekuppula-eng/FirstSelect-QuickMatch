from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from first_select_quickmatch.core.models import RequirementHints


@dataclass
class SQLQuery:
    sql: str
    params: list[Any]


class PostgresQueryBuilder:
    """Builds parameterized PostgreSQL SQL for retrieval-agent facility fetches."""

    BASE_SELECT = (
        "SELECT f.*, "
        "jsonb_build_object("
        "'name', s.name, "
        "'star_rating', s.star_rating, "
        "'verified', COALESCE(s.verified, false), "
        "'total_reviews', COALESCE(s.total_reviews, 0)"
        ") AS suppliers "
        "FROM public.facilities f "
        "JOIN public.suppliers s ON s.id = f.supplier_id"
    )

    def build(self, hints: RequirementHints, limit: int = 200) -> SQLQuery:
        where: list[str] = []
        params: list[Any] = []

        if hints.service_type:
            where.append("(f.service_type = %s OR f.service_type = 'both')")
            params.append(hints.service_type)

        if hints.location:
            where.append("LOWER(f.location) LIKE %s")
            params.append(f"%{hints.location.lower()}%")

        if hints.is_food_grade:
            where.append("f.is_food_grade = TRUE")

        if hints.is_hazmat:
            where.append("f.is_hazmat = TRUE")

        if hints.security_level:
            where.append(
                "CASE f.security_level "
                "WHEN 'standard' THEN 0 "
                "WHEN 'enhanced' THEN 1 "
                "WHEN 'high' THEN 2 "
                "ELSE 0 END >= "
                "CASE %s "
                "WHEN 'standard' THEN 0 "
                "WHEN 'enhanced' THEN 1 "
                "WHEN 'high' THEN 2 "
                "ELSE 0 END"
            )
            params.append(hints.security_level)

        if hints.integration_methods:
            where.append("f.integration_methods && %s::text[]")
            params.append(hints.integration_methods)

        if hints.required_sqft is not None:
            where.append("(f.max_sqft IS NULL OR f.max_sqft >= %s)")
            params.append(hints.required_sqft)

        if hints.order_volume is not None:
            where.append("(f.min_order_volume IS NULL OR f.min_order_volume <= %s)")
            params.append(hints.order_volume)
            where.append("(f.max_order_volume IS NULL OR f.max_order_volume >= %s)")
            params.append(hints.order_volume)

        if hints.temperature_min is not None:
            where.append("(f.temperature_range_min IS NULL OR f.temperature_range_min <= %s)")
            params.append(hints.temperature_min)

        if hints.temperature_max is not None:
            where.append("(f.temperature_range_max IS NULL OR f.temperature_range_max >= %s)")
            params.append(hints.temperature_max)

        query = [self.BASE_SELECT]
        if where:
            query.append("WHERE " + " AND ".join(where))

        query.append("ORDER BY s.star_rating DESC NULLS LAST, s.total_reviews DESC NULLS LAST")
        query.append("LIMIT %s")
        params.append(limit)

        return SQLQuery(sql="\n".join(query), params=params)
