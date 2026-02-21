from __future__ import annotations

import math
from typing import Any

from first_select_quickmatch.core.models import FacilityMatch, RequirementHints

SECURITY_LEVELS = {"standard": 0, "enhanced": 1, "high": 2}


def passes_tier1(supplier: dict[str, Any], hints: RequirementHints) -> bool:
    if hints.is_food_grade and not supplier.get("is_food_grade"):
        return False
    if hints.is_hazmat and not supplier.get("is_hazmat"):
        return False

    if hints.temperature_min is not None or hints.temperature_max is not None:
        smin = supplier.get("temperature_range_min")
        smax = supplier.get("temperature_range_max")
        if smin is not None and smax is not None:
            if hints.temperature_min is not None and smin > hints.temperature_min:
                return False
            if hints.temperature_max is not None and smax < hints.temperature_max:
                return False

    if hints.security_level:
        required = SECURITY_LEVELS.get(hints.security_level, 0)
        supplied = SECURITY_LEVELS.get(supplier.get("security_level", "standard"), 0)
        if supplied < required:
            return False

    if hints.integration_methods:
        methods = [m.lower() for m in supplier.get("integration_methods", [])]
        if not any(m in methods for m in hints.integration_methods):
            return False

    return True


def score_tier2(supplier: dict[str, Any], hints: RequirementHints) -> tuple[bool, list[float]]:
    scores: list[float] = []

    if hints.required_sqft is not None:
        max_sqft = supplier.get("max_sqft")
        if max_sqft is None or max_sqft < hints.required_sqft:
            return False, []
        scores.append(max(0, 100 * (1 - abs(max_sqft - hints.required_sqft) / 50000)))

    if hints.order_volume is not None:
        min_vol = supplier.get("min_order_volume")
        max_vol = supplier.get("max_order_volume")
        if min_vol is not None and hints.order_volume < min_vol:
            return False, []
        if max_vol is not None and hints.order_volume > max_vol:
            return False, []
        if max_vol is not None:
            scores.append(max(0, 100 * (1 - abs(max_vol - hints.order_volume) / 10000)))

    if hints.temperature_min is not None and supplier.get("temperature_range_min") is not None:
        dev = abs(supplier["temperature_range_min"] - hints.temperature_min)
        scores.append(100 * math.exp(-3 * dev / 30))

    if hints.temperature_preferred and supplier.get("temperature_range_min") is not None:
        scores.append(80)

    if supplier.get("on_time_rate") is not None:
        scores.append(max(0, float(supplier["on_time_rate"])))

    return True, scores


def score_tier3(supplier: dict[str, Any], hints: RequirementHints) -> list[float]:
    scores: list[float] = []

    def overlap_score(req: list[str], values: list[str]) -> float:
        if not req:
            return -1
        lower = [v.lower() for v in values]
        hit = sum(1 for r in req if any(r in v for v in lower))
        return (hit / len(req)) * 100

    if hints.vas_services:
        scores.append(overlap_score(hints.vas_services, supplier.get("vas_services", [])))
    if hints.certifications:
        scores.append(overlap_score(hints.certifications, supplier.get("certifications", [])))
    if hints.inbound:
        scores.append(overlap_score(hints.inbound, supplier.get("inbound_capabilities", [])))
    if hints.outbound:
        scores.append(overlap_score(hints.outbound, supplier.get("outbound_capabilities", [])))

    if hints.volume_pattern:
        scores.append(100 if supplier.get("volume_pattern") == hints.volume_pattern else 0)
    if hints.term_type:
        scores.append(100 if supplier.get("term_type") == hints.term_type else 0)
    if hints.location and supplier.get("location"):
        scores.append(100 if hints.location in supplier["location"].lower() else 0)

    return [s for s in scores if s >= 0]


def compute_coverage(supplier: dict[str, Any], hints: RequirementHints) -> float:
    checks = [
        (hints.inbound, supplier.get("inbound_capabilities")),
        (hints.outbound, supplier.get("outbound_capabilities")),
        (hints.certifications, supplier.get("certifications")),
        (hints.vas_services, supplier.get("vas_services")),
        (hints.required_sqft, supplier.get("max_sqft")),
        (hints.order_volume, supplier.get("max_order_volume")),
        (hints.location, supplier.get("location")),
    ]
    requested = 0
    present = 0
    for hint, value in checks:
        has_hint = bool(hint) if not isinstance(hint, (int, float)) else hint is not None
        if has_hint:
            requested += 1
            if value is not None and value != []:
                present += 1
    return 1.0 if requested == 0 else present / requested


def build_reasons(supplier: dict[str, Any], hints: RequirementHints) -> list[str]:
    reasons: list[str] = []
    if hints.location and hints.location in (supplier.get("location", "").lower()):
        reasons.append(f"Located in {supplier.get('location')}")
    if hints.temperature_preferred and supplier.get("temperature_range_min") is not None:
        reasons.append(
            f"Temperature-controlled: {supplier.get('temperature_range_min')}°F to {supplier.get('temperature_range_max')}°F"
        )
    if supplier.get("on_time_rate") is not None:
        reasons.append(f"On-time rate: {supplier.get('on_time_rate')}%")
    if hints.certifications and supplier.get("certifications"):
        reasons.append("Certifications overlap")
    if not reasons:
        reasons.append("General warehouse capabilities")
    return reasons


def search_suppliers(facilities: list[dict[str, Any]], hints: RequirementHints) -> list[FacilityMatch]:
    def score_pipeline(rows: list[dict[str, Any]], relaxed: bool) -> list[FacilityMatch]:
        out: list[FacilityMatch] = []
        for f in rows:
            if not passes_tier1(f, hints if not relaxed else RequirementHints(**{**hints.__dict__, "temperature_min": None, "temperature_max": None})):
                continue
            pass2, tier2 = score_tier2(f, hints)
            if not pass2:
                continue
            tier3 = score_tier3(f, hints)
            bumped = sum(tier2) / len(tier2) if tier2 else 0
            regular = sum(tier3) / len(tier3) if tier3 else 0
            composite = 0.60 * bumped + 0.40 * regular if tier2 else regular
            coverage = compute_coverage(f, hints)
            out.append(
                FacilityMatch(
                    id=str(f["id"]),
                    facility_name=f.get("facility_name", "Unknown"),
                    company_name=f.get("suppliers", {}).get("name", "Unknown"),
                    location=f.get("location", ""),
                    star_rating=float(f.get("suppliers", {}).get("star_rating", 0) or 0),
                    match_percentage=max(0, min(100, round(composite))),
                    confidence_score=round(coverage * 100),
                    low_confidence=coverage < 0.4,
                    relaxed_match=relaxed,
                    match_reasons=build_reasons(f, hints),
                    inbound_capabilities=f.get("inbound_capabilities", []),
                    outbound_capabilities=f.get("outbound_capabilities", []),
                    certifications=f.get("certifications", []),
                    verified=bool(f.get("suppliers", {}).get("verified", False)),
                    review_count=int(f.get("suppliers", {}).get("total_reviews", 0) or 0),
                )
            )
        out.sort(key=lambda x: (x.match_percentage, x.confidence_score), reverse=True)
        return out

    pass1 = score_pipeline(facilities, relaxed=False)
    if pass1:
        return pass1
    pass2 = score_pipeline(facilities, relaxed=True)
    if pass2:
        return pass2
    return []
