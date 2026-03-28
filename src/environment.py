from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from .graders import grade_action, grade_episode
from .models import EnvironmentState, StepResult, TriageAction
from .tasks import TaskDefinition, build_tasks


class IncidentTriageEnv:
    def __init__(self) -> None:
        self.tasks: Dict[str, TaskDefinition] = build_tasks()
        self._current_task: TaskDefinition | None = None
        self._state: EnvironmentState | None = None
        self._per_ticket_scores: Dict[str, float] = {}

    def reset(self, task_id: str = "easy") -> EnvironmentState:
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task_id: {task_id}")
        self._current_task = self.tasks[task_id]
        self._per_ticket_scores = {}
        self._state = EnvironmentState(
            task_id=self._current_task.task_id,
            turn=0,
            max_turns=self._current_task.max_turns,
            tickets=deepcopy(self._current_task.tickets),
            score_so_far=0.0,
            done=False,
            history=[],
        )
        return self.state()

    def state(self) -> EnvironmentState:
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        return deepcopy(self._state)

    def step(self, action: TriageAction) -> StepResult:
        if self._state is None or self._current_task is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        if self._state.done:
            raise RuntimeError("Episode already done. Call reset() to start a new episode.")

        ticket = next((t for t in self._state.tickets if t.ticket_id == action.ticket_id), None)
        if ticket is None:
            return StepResult(
                reward=-0.2,
                done=False,
                info={"error": f"ticket_id {action.ticket_id} not found"},
                state=self.state(),
            )

        expected = self._current_task.rubric[ticket.ticket_id]
        action_score = grade_action(action, expected)

        ticket.category = action.category
        ticket.priority = action.priority
        ticket.owner = action.owner
        ticket.response_sent = bool(action.send_response)
        ticket.escalated = bool(action.escalate)
        ticket.closed = bool(action.close_ticket)
        ticket.minutes_to_sla_breach = max(0, ticket.minutes_to_sla_breach - 10)

        self._per_ticket_scores[ticket.ticket_id] = max(
            self._per_ticket_scores.get(ticket.ticket_id, 0.0), action_score
        )

        response_bonus = 0.05 if action.send_response else -0.05
        urgency_penalty = 0.0
        if ticket.minutes_to_sla_breach <= 30 and action.priority.value in {"low", "medium"}:
            urgency_penalty = -0.1

        reward = max(-1.0, min(1.0, action_score + response_bonus + urgency_penalty))
        self._state.turn += 1
        self._state.history.append(f"ticket={ticket.ticket_id} reward={reward:.3f}")

        turn_limit_hit = self._state.turn >= self._state.max_turns


        all_tickets_sufficient = all(
            self._per_ticket_scores.get(t.ticket_id, 0.0) >= 0.9 for t in self._state.tickets
        )
        self._state.done = turn_limit_hit or all_tickets_sufficient


        per_ticket_scores_all = [
            self._per_ticket_scores.get(t.ticket_id, 0.0) for t in self._state.tickets
        ]
        self._state.score_so_far = grade_episode(per_ticket_scores_all)

        return StepResult(
            reward=round(reward, 4),
            done=self._state.done,
            info={
                "task_id": self._state.task_id,
                "turn": self._state.turn,
                "ticket_score": round(action_score, 4),
                "episode_score": self._state.score_so_far,
            },
            state=self.state(),
        )
