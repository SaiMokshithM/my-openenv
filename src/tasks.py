from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .models import Ticket


@dataclass(frozen=True)
class TaskDefinition:
    task_id: str
    difficulty: str
    objective: str
    max_turns: int
    tickets: List[Ticket]
    rubric: Dict[str, Dict[str, object]]


def build_tasks() -> Dict[str, TaskDefinition]:
    easy_tickets = [
        Ticket(
            ticket_id="E-101",
            title="Cannot access dashboard",
            description="New hire cannot log in after account creation.",
            customer_tier="standard",
            minutes_to_sla_breach=240,
        )
    ]
    easy_rubric = {
        "E-101": {
            "category": "access",
            "priority": "medium",
            "owner": "identity-team",
            "needs_escalation": False,
            "should_close": False,
        }
    }

    medium_tickets = [
        Ticket(
            ticket_id="M-201",
            title="Suspicious password reset emails",
            description="""User Report:
Hi Support, I've received 14 password reset emails in the last hour but I didn't request any.
Headers show:
Received: from 192.168.1.144 (unknown [185.14.22.1])
X-Originating-IP: [185.14.22.1]
Is my account compromised?""",
            customer_tier="enterprise",
            minutes_to_sla_breach=60,
        ),
        Ticket(
            ticket_id="M-202",
            title="Invoice line item mismatch",
            description="""Finance team escalation:
We noticed a discrepancy in the March invoice for customer ACME.
API calls billed: 1,450,200 ($145.02)
Metrics DB shows: 1,300,000 calls.
Please investigate the 150k delta. Attached log snippet:
[BILLING-JOB] WARN: Retrying batch id=99x2 due to lock timeout.
[BILLING-JOB] INFO: Batch id=99x2 committed successfully.""",
            customer_tier="enterprise",
            minutes_to_sla_breach=360,
        ),
    ]
    medium_rubric = {
        "M-201": {
            "category": "security",
            "priority": "high",
            "owner": "security-team",
            "needs_escalation": True,
            "should_close": False,
        },
        "M-202": {
            "category": "billing",
            "priority": "medium",
            "owner": "billing-team",
            "needs_escalation": False,
            "should_close": False,
        },
    }

    hard_tickets = [
        Ticket(
            ticket_id="H-301",
            title="Checkout latency spikes and 5xx errors",
            description="""PagerDuty Alert:
Service: checkout-api-eu
Metric: P95 Latency > 8000ms
Logs:
2026-03-26T10:14:22Z ERR [db-pool] Connection timeout acquiring connection from primary-db-eu-west-1
2026-03-26T10:14:25Z FATAL [checkout-flow] Unable to persist order id=88192a. Payment captured but DB save failed.
2026-03-26T10:15:01Z WARN [healthcheck] primary-db-eu-west-1 response time 9500ms
Impact: Premium users are failing to checkout. Revenue dropping ~5% WoW.""",
            customer_tier="premium",
            minutes_to_sla_breach=35,
        ),
        Ticket(
            ticket_id="H-302",
            title="Data export fails for APAC",
            description="""Customer Complaint (Enterprise Support Thread):
> On 03/25, Bob wrote: The nightly data export to S3 failed again. We need this for our compliance audit tomorrow!
> On 03/25, Support wrote: Investigating. I see a timeout in the worker.
> On 03/26, Bob wrote: It failed AGAIN tonight. What is going on?

Worker Logs:
Exception: MemoryError in parquet.write_table()
Payload size: 14.2GB
Instance: worker-mem-optimised-4x""",
            customer_tier="enterprise",
            minutes_to_sla_breach=50,
        ),
        Ticket(
            ticket_id="H-303",
            title="Unauthorized admin role assignment",
            description="""Security System Auto-Alert:
Severity: CRITICAL
Event: ROLE_GRANT
Subject: admin-role
Target: svc-account-deployer
Actor: jsmith@company.com (IP: 44.22.11.9)
Notes: jsmith's normal IP range is 10.x.x.x. The grant bypassed MFA via an legacy API token. Action requires immediate verification.""",
            customer_tier="enterprise",
            minutes_to_sla_breach=20,
        ),
        Ticket(
            ticket_id="H-304",
            title="Coffee machine in breakroom 4 is broken",
            description="""Hey IT support,
The espresso machine on the 4th floor is just blinking red and won't brew.
Can someone come fix this ASAP? I literally cannot function without my morning double shot.
Thanks,
Dave (Sales)""",
            customer_tier="standard",
            minutes_to_sla_breach=2880,
        ),
    ]
    hard_rubric = {
        "H-301": {
            "category": "outage",
            "priority": "high",
            "owner": "platform-sre",
            "needs_escalation": True,
            "should_close": False,
        },
        "H-302": {
            "category": "bug",
            "priority": "medium",
            "owner": "data-platform",
            "needs_escalation": False,
            "should_close": False,
        },
        "H-303": {
            "category": "security",
            "priority": "critical",
            "owner": "security-team",
            "needs_escalation": True,
            "should_close": False,
        },
        "H-304": {
            "category": "noise",
            "priority": "low",
            "owner": "facilities-team",
            "needs_escalation": False,
            "should_close": True,
        },
    }

    return {
        "easy": TaskDefinition(
            task_id="easy",
            difficulty="easy",
            objective="Correctly triage one low-risk access request.",
            max_turns=3,
            tickets=easy_tickets,
            rubric=easy_rubric,
        ),
        "medium": TaskDefinition(
            task_id="medium",
            difficulty="medium",
            objective="Triage two tickets including log analysis and security concerns.",
            max_turns=6,
            tickets=medium_tickets,
            rubric=medium_rubric,
        ),
        "hard": TaskDefinition(
            task_id="hard",
            difficulty="hard",
            objective="Handle mixed incidents under tight SLA pressure, including complex outages and a noise/spam ticket.",
            max_turns=12,
            tickets=hard_tickets,
            rubric=hard_rubric,
        ),
    }
