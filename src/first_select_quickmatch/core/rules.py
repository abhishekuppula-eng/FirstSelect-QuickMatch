from __future__ import annotations

import re
from typing import Iterable

from .models import ChatMessage, ConversationState, RequirementHints


def count_user_messages(messages: Iterable[ChatMessage]) -> int:
    return sum(1 for m in messages if m.role == "user")


def detect_fatigue(user_message: str) -> bool:
    lower = user_message.lower().strip()
    fatigue_patterns = [
        "i don't know", "i dont know", "not sure", "no idea",
        "too many questions", "just find me", "just show me",
        "whatever works", "anything is fine", "skip", "idk",
        "doesn't matter", "doesnt matter",
    ]
    if len(lower) < 5 and lower not in {"yes", "no", "ok"}:
        return True
    return any(p in lower for p in fatigue_patterns)


def detect_confirmation(messages: list[ChatMessage]) -> bool:
    already_matched = any(
        m.role == "assistant" and "<!-- MATCH_COMPLETE -->" in m.content for m in messages
    )
    if already_matched:
        return True

    if len(messages) < 4:
        return False

    last_assistant_idx = -1
    for i in range(len(messages) - 2, -1, -1):
        if messages[i].role == "assistant":
            last_assistant_idx = i
            break
    if last_assistant_idx < 0:
        return False

    assistant_msg = messages[last_assistant_idx].content.lower()
    has_summary = any(k in assistant_msg for k in [
        "requirement summary", "requirements summary", "does this look right", "confirm",
        "adjust anything", "finding your matches", "ready to search", "ready to find",
    ])
    if not has_summary:
        return False

    last_user = messages[-1]
    if last_user.role != "user":
        return False

    user_lower = last_user.content.lower().strip()
    affirmatives = [
        "yes", "confirmed", "looks good", "correct", "go ahead", "proceed", "perfect", "ok",
        "search", "find suppliers", "show results", "find matches",
    ]
    return any(a in user_lower for a in affirmatives)


def extract_requirement_hints(messages: list[ChatMessage]) -> RequirementHints:
    text = "\n".join(m.content for m in messages).lower()
    hints = RequirementHints()

    for loc in ["midwest", "northeast", "southeast", "west coast", "texas", "california", "new york"]:
        if loc in text:
            hints.location = loc
            break

    inbound_types = ["pallet", "carton", "gaylord", "crate", "container", "floor-loaded"]
    outbound_types = ["parcel", "same carton", "new carton", "same pallet", "new pallet"]
    hints.inbound = [x for x in inbound_types if x in text]
    hints.outbound = [x for x in outbound_types if x in text]

    special_types = ["temperature", "cold", "frozen", "refrigerated", "hazmat", "fragile", "food grade", "fda"]
    hints.special_handling = [x for x in special_types if x in text]
    cert_types = ["iso", "soc", "fda", "gmp", "haccp", "c-tpat", "organic"]
    hints.certifications = [x for x in cert_types if x in text]

    if "food grade" in text or "food-grade" in text:
        hints.is_food_grade = True
    if "hazmat" in text or "hazardous" in text:
        hints.is_hazmat = True

    temp_match = re.search(r"(-?\d+)\s*°?\s*[fc]?\s*(?:to|-)\s*(-?\d+)\s*°?\s*[fc]?", text)
    if temp_match:
        hints.temperature_min = float(temp_match.group(1))
        hints.temperature_max = float(temp_match.group(2))
    elif any(k in text for k in ["frozen", "cold storage", "refrigerated", "cold"]):
        hints.temperature_preferred = True

    if "high security" in text:
        hints.security_level = "high"
    elif "enhanced security" in text:
        hints.security_level = "enhanced"

    vas_types = ["kitting", "returns", "quality inspection", "customization", "marketplace prep", "cross-docking"]
    hints.vas_services = [x for x in vas_types if x in text]

    for keyword, val in {
        "seasonal": "seasonal_spikes", "steady": "steady", "event": "event_spikes", "growing": "growth"
    }.items():
        if keyword in text:
            hints.volume_pattern = val
            break

    for keyword, val in {
        "long term": "long_term", "annual": "annual_seasonal", "short term": "short_term_project", "trial": "trial_pilot"
    }.items():
        if keyword in text:
            hints.term_type = val
            break

    sqft_match = re.search(r"(\d[\d,]*)\s*(?:sq\s*ft|square\s*feet|sqft)", text)
    if sqft_match:
        hints.required_sqft = float(sqft_match.group(1).replace(",", ""))

    vol_match = re.search(r"(\d[\d,]*)\s*(?:orders?|units?)\s*(?:per|/)\s*month", text)
    if vol_match:
        hints.order_volume = int(vol_match.group(1).replace(",", ""))

    hints.integration_methods = [x for x in ["api", "edi", "sftp", "csv", "webhook"] if x in text]

    warehouse_signals = ["warehouse", "storage", "fulfillment", "3pl", "inventory", "cold storage"]
    transport_signals = ["transport", "trucking", "freight", "shipping", "carrier", "ltl", "ftl"]
    has_warehouse = any(s in text for s in warehouse_signals)
    has_transport = any(s in text for s in transport_signals)
    if has_warehouse and has_transport:
        hints.service_type = "both"
    elif has_warehouse:
        hints.service_type = "warehouse"
    elif has_transport:
        hints.service_type = "transport"

    return hints


def build_conversation_state(messages: list[ChatMessage], elapsed_minutes: float = 0.0) -> ConversationState:
    question_count = count_user_messages(messages)
    latest = messages[-1].content if messages else ""
    fatigue = detect_fatigue(latest)
    confirmed = detect_confirmation(messages)
    timekeeper_triggered = elapsed_minutes > 6 or question_count > 8 or fatigue
    return ConversationState(
        question_count=question_count,
        fatigue_detected=fatigue,
        is_confirmed=confirmed,
        elapsed_minutes=elapsed_minutes,
        timekeeper_triggered=timekeeper_triggered,
    )
