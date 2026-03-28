---
title: OpenEnv Incident Triage
emoji: 🚨
colorFrom: blue
colorTo: red
sdk: gradio
app_file: app.py
pinned: false
---
# Incident Triage OpenEnv

This project provides a real-world OpenEnv-style environment for training and evaluating agents on **IT incident triage**.

Agents receive live ticket state, then choose triage actions:
- classify issue category,
- assign priority,
- route to owning team,
- decide whether escalation is required.

The environment supports progressive difficulty and deterministic grading with partial progress rewards.
https://huggingface.co/spaces/saimokshith/openenv
## Why this is useful

Incident triage is a practical operational workflow used by support, SRE, and security teams. This environment measures whether an agent can make reliable, high-stakes workflow decisions under SLA pressure.

## API

The environment follows `reset()` / `step()` / `state()` methods:

- `reset(task_id: str) -> EnvironmentState`
- `state() -> EnvironmentState`
- `step(action: TriageAction) -> StepResult`

Reference implementation entrypoint: `src.environment:IncidentTriageEnv`

## Action space

Typed action model (`TriageAction`):
- `ticket_id: str`
- `category: access|security|billing|outage|bug`
- `priority: low|medium|high|critical`
- `owner: str`
- `send_response: bool`
- `escalate: bool`
- `close_ticket: bool`

## Observation space

Typed state model (`EnvironmentState`):
- task metadata (`task_id`, `turn`, `max_turns`)
- full ticket list with SLA and triage fields
- running score (`score_so_far`)
- terminal flag (`done`)
- short textual action history (`history`)

## Tasks and graders

Three deterministic tasks with increasing difficulty:

1. **easy**: single access issue
2. **medium**: mixed security + billing queue
3. **hard**: multi-ticket outage/security/bug triage with tighter SLA windows

Per-step grading (`0.0` to `1.0`) scores:
- category correctness,
- priority correctness,
- owner assignment,
- escalation decision,
- close decision.

Episode score is the average of best per-ticket scores.

## Reward shaping

`reward = action_score + response_bonus + urgency_penalty` (clipped to `[-1.0, 1.0]`)

- `action_score` gives dense partial credit (0.0-1.0)
- `response_bonus` rewards timely customer acknowledgement
- `urgency_penalty` discourages under-prioritizing near-breach incidents

## Local setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Run baseline:

```bash
python baseline.py
```

Expected deterministic baseline output:

```text
easy: 1.0000
medium: 1.0000
hard: 1.0000
```

Run API server:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 7860
```

## Docker

Build:

```bash
docker build -t incident-triage-openenv .
```

Run:

```bash
docker run --rm -p 7860:7860 incident-triage-openenv
```

## Hugging Face Spaces deployment

1. Create a new Space using **Docker** SDK.
2. Push this repository content.
3. Space will build from `Dockerfile` and expose port `7860`.
4. Health check endpoint: `GET /health`.

## Files

- `openenv.yaml` - environment metadata/spec
- `src/models.py` - typed state/action/result models
- `src/environment.py` - core environment state machine
- `src/graders.py` - deterministic task graders
- `src/tasks.py` - task scenarios and rubrics
- `src/main.py` - HTTP wrapper for Space runtime
- `baseline.py` - reproducible baseline runner
