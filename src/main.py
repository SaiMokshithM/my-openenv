from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .environment import IncidentTriageEnv
from .models import EnvironmentState, StepResult, TriageAction
from .tasks import build_tasks

app = FastAPI(title="OpenEnv Incident Triage Environment", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = IncidentTriageEnv()
_tasks = build_tasks()






class ResetRequest(BaseModel):
    task_id: str = "easy"


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str


class TaskSummary(BaseModel):
    task_id: str
    difficulty: str
    objective: str
    max_turns: int
    ticket_count: int


class TicketInfo(BaseModel):
    ticket_id: str
    title: str
    description: str
    customer_tier: str
    minutes_to_sla_breach: int


class TaskDetail(BaseModel):
    task_id: str
    difficulty: str
    objective: str
    max_turns: int
    tickets: List[TicketInfo]






@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskSummary])
def list_tasks() -> List[TaskSummary]:
    """Return metadata for all available tasks."""
    return [
        TaskSummary(
            task_id=t.task_id,
            difficulty=t.difficulty,
            objective=t.objective,
            max_turns=t.max_turns,
            ticket_count=len(t.tickets),
        )
        for t in _tasks.values()
    ]


@app.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task(task_id: str) -> TaskDetail:
    """Return full task detail including ticket descriptions (rubric answers not exposed)."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {task_id}")
    t = _tasks[task_id]
    return TaskDetail(
        task_id=t.task_id,
        difficulty=t.difficulty,
        objective=t.objective,
        max_turns=t.max_turns,
        tickets=[
            TicketInfo(
                ticket_id=tk.ticket_id,
                title=tk.title,
                description=tk.description,
                customer_tier=tk.customer_tier,
                minutes_to_sla_breach=tk.minutes_to_sla_breach,
            )
            for tk in t.tickets
        ],
    )


@app.post("/reset", response_model=EnvironmentState)
def reset(req: ResetRequest) -> EnvironmentState:
    try:
        return env.reset(task_id=req.task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/state", response_model=EnvironmentState)
def state() -> EnvironmentState:
    try:
        return env.state()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/step", response_model=StepResult)
def step(action: TriageAction) -> StepResult:
    try:
        return env.step(action)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatResponse)
def mock_chat(req: ChatRequest) -> ChatResponse:
    """A mock chat endpoint so the frontend can display 'model responses' before an actual LLM is wired up."""

    prompt = req.prompt.lower()
    if "hello" in prompt or "hi" in prompt:
        return ChatResponse(response="Hello! I am your AI triage agent. Which task should we look at?")
    elif "reset" in prompt:
         return ChatResponse(response="To reset the environment, please click the 'Start Task' button or use the /reset backend endpoint.")
    else:
        return ChatResponse(response=(
            "I see your prompt: _'" + req.prompt + "'_. "
            "In the future, I will convert this into a JSON Action and call `/step` on the environment!"
        ))
