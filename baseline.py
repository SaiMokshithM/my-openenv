from __future__ import annotations

from src.environment import IncidentTriageEnv
from src.models import Category, Priority, TriageAction


def run_baseline(task_id: str) -> float:
    env = IncidentTriageEnv()
    state = env.reset(task_id)

    policy = {
        "E-101": TriageAction(
            ticket_id="E-101",
            category=Category.access,
            priority=Priority.medium,
            owner="identity-team",
            send_response=True,
            escalate=False,
            close_ticket=False,
        ),
        "M-201": TriageAction(
            ticket_id="M-201",
            category=Category.security,
            priority=Priority.high,
            owner="security-team",
            send_response=True,
            escalate=True,
            close_ticket=False,
        ),
        "M-202": TriageAction(
            ticket_id="M-202",
            category=Category.billing,
            priority=Priority.medium,
            owner="billing-team",
            send_response=True,
            escalate=False,
            close_ticket=False,
        ),
        "H-301": TriageAction(
            ticket_id="H-301",
            category=Category.outage,
            priority=Priority.high,
            owner="platform-sre",
            send_response=True,
            escalate=True,
            close_ticket=False,
        ),
        "H-302": TriageAction(
            ticket_id="H-302",
            category=Category.bug,
            priority=Priority.medium,
            owner="data-platform",
            send_response=True,
            escalate=False,
            close_ticket=False,
        ),
        "H-303": TriageAction(
            ticket_id="H-303",
            category=Category.security,
            priority=Priority.critical,
            owner="security-team",
            send_response=True,
            escalate=True,
            close_ticket=False,
        ),
        "H-304": TriageAction(
            ticket_id="H-304",
            category=Category.noise,
            priority=Priority.low,
            owner="facilities-team",
            send_response=False,
            escalate=False,
            close_ticket=True,
        ),
    }

    for ticket in state.tickets:
        if state.done:
            break
        if ticket.ticket_id not in policy:
            continue
        result = env.step(policy[ticket.ticket_id])
        state = result.state

    return state.score_so_far


if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        score = run_baseline(task)
        print(f"{task}: {score:.4f}")
