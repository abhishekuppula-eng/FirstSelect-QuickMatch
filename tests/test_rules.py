from first_select_quickmatch.core.models import ChatMessage
from first_select_quickmatch.core.rules import build_conversation_state, detect_confirmation, extract_requirement_hints


def test_extract_hints_detects_service_and_temperature_preference():
    messages = [ChatMessage(role="user", content="Need cold storage warehouse in Texas with API integration")]
    hints = extract_requirement_hints(messages)
    assert hints.service_type == "warehouse"
    assert hints.temperature_preferred is True
    assert hints.location == "texas"
    assert "api" in hints.integration_methods


def test_detect_confirmation_true_after_summary_prompt_and_affirmative():
    messages = [
        ChatMessage(role="user", content="Need 3PL"),
        ChatMessage(role="assistant", content="Requirement summary ... does this look right?"),
        ChatMessage(role="user", content="Yes, proceed and find suppliers"),
        ChatMessage(role="assistant", content="Requirement summary confirmed. Ready to search?"),
        ChatMessage(role="user", content="search now"),
    ]
    assert detect_confirmation(messages) is True


def test_timekeeper_triggered_by_question_budget():
    messages = [ChatMessage(role="user", content=f"q{i}") for i in range(9)]
    state = build_conversation_state(messages, elapsed_minutes=2.0)
    assert state.timekeeper_triggered is True
