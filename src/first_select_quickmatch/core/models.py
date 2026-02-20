from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class RequirementHints:
    location: str | None = None
    inbound: list[str] = field(default_factory=list)
    outbound: list[str] = field(default_factory=list)
    special_handling: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    service_type: str | None = None
    volume_pattern: str | None = None
    term_type: str | None = None
    vas_services: list[str] = field(default_factory=list)
    is_food_grade: bool | None = None
    is_hazmat: bool | None = None
    security_level: str | None = None
    integration_methods: list[str] = field(default_factory=list)
    temperature_min: float | None = None
    temperature_max: float | None = None
    temperature_preferred: bool | None = None
    required_sqft: float | None = None
    order_volume: int | None = None


@dataclass
class FacilityMatch:
    id: str
    facility_name: str
    company_name: str
    location: str
    star_rating: float
    match_percentage: int
    confidence_score: int
    low_confidence: bool
    relaxed_match: bool
    match_reasons: list[str]
    inbound_capabilities: list[str]
    outbound_capabilities: list[str]
    certifications: list[str]
    verified: bool
    review_count: int


@dataclass
class ConversationState:
    question_count: int
    fatigue_detected: bool
    is_confirmed: bool
    elapsed_minutes: float
    timekeeper_triggered: bool


@dataclass
class AgentResult:
    mode: str
    response_text: str
    tool_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
