from __future__ import annotations

from typing import Dict, List

from .models import TriageAction


def grade_action(action: TriageAction, expected: Dict[str, object]) -> float:
    score = 0.0
    if action.category.value == expected["category"]:
        score += 0.35
    if action.priority.value == expected["priority"]:
        score += 0.25
    if action.owner == expected["owner"]:
        score += 0.2
    if bool(action.escalate) == bool(expected["needs_escalation"]):
        score += 0.1
    if bool(action.close_ticket) == bool(expected["should_close"]):
        score += 0.1
    return max(0.0, min(1.0, score))


def grade_episode(per_ticket_scores: List[float]) -> float:
    if not per_ticket_scores:
        return 0.0
    return round(sum(per_ticket_scores) / len(per_ticket_scores), 4)
