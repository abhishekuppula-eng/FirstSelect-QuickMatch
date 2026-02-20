from __future__ import annotations

from first_select_quickmatch.core.models import ConversationState


class TimekeeperAgent:
    """Policy agent: decides when requirement phase must force summary."""

    def should_force_summarize(self, state: ConversationState) -> bool:
        return state.timekeeper_triggered
