from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Category(str, Enum):
    access = "access"
    security = "security"
    billing = "billing"
    outage = "outage"
    bug = "bug"
    noise = "noise"


class Ticket(BaseModel):
    ticket_id: str
    title: str
    description: str
    customer_tier: str
    minutes_to_sla_breach: int
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    owner: Optional[str] = None
    response_sent: bool = False
    escalated: bool = False
    closed: bool = False


class EnvironmentState(BaseModel):
    task_id: str
    turn: int
    max_turns: int
    tickets: List[Ticket]
    score_so_far: float = 0.0
    done: bool = False
    history: List[str] = Field(default_factory=list)


class TriageAction(BaseModel):
    ticket_id: str
    category: Category
    priority: Priority
    owner: str
    send_response: bool = True
    escalate: bool = False
    close_ticket: bool = False


class StepResult(BaseModel):
    reward: float
    done: bool
    info: Dict[str, float | str]
    state: EnvironmentState
