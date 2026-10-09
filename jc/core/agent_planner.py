"""Planning utilities for JC. Planning is not execution."""

import json
import re
from typing import Any


ALLOWED_AGENT_ROLES = {
    "master", "research", "real_estate", "finance", "accountant",
    "developer", "marketing", "operations", "legal_compliance", "general",
}


def build_planning_prompt(goal: str, language: str = "English") -> str:
    """Ask the configured model for a bounded, structured, reviewable plan."""
    return (
        "You are JC, a supervised multi-agent planning system. Do not claim to execute tools. "
        "Create a practical plan for the founder's goal. Return ONLY a JSON object with keys "
        "title, summary, steps. steps must contain 1 to 8 objects, each with title, agent, "
        "description. agent must be one of: master, research, real_estate, finance, accountant, "
        "developer, marketing, operations, legal_compliance, general. Each step must be a "
        "proposed task, not a claim that work has already happened. Mark risky external actions "
        "such as purchases, publishing, sending messages, account changes, code deployment, or "
        "destructive actions as steps that require founder approval. Do not request or include "
        "passwords, API keys, bank credentials, or other secrets. Reply language: " + language + ".\n\n"
        "Founder goal:\n" + goal.strip()
    )


def parse_plan_response(raw: str) -> dict[str, Any]:
    """Parse and validate a model-produced plan before saving it."""
    candidate = raw.strip()
    fence = chr(96) * 3
    fenced = re.fullmatch(re.escape(fence) + r"(?:json)?\s*(.*?)\s*" + re.escape(fence), candidate, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1).strip()
    try:
        payload = json.loads(candidate)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("The AI planner did not return valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("The AI planner response must be a JSON object.")

    title = payload.get("title")
    summary = payload.get("summary")
    steps = payload.get("steps")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Plan title is required.")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("Plan summary is required.")
    if not isinstance(steps, list) or not steps:
        raise ValueError("The plan must contain at least one step.")
    if len(steps) > 8:
        raise ValueError("The plan cannot contain more than 8 steps.")

    normalized = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError(f"Step {index} must be a JSON object.")
        step_title = step.get("title")
        agent = step.get("agent")
        description = step.get("description")
        if not isinstance(step_title, str) or not step_title.strip():
            raise ValueError(f"Step {index} title is required.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Step {index} description is required.")
        if not isinstance(agent, str) or agent not in ALLOWED_AGENT_ROLES:
            raise ValueError(f"Step {index} agent must use an approved specialist role.")
        normalized.append({
            "id": index,
            "title": step_title.strip()[:160],
            "agent": agent,
            "description": description.strip()[:2000],
            "status": "pending_approval",
            "requires_approval": True,
            "actions_executed": False,
        })

    return {
        "title": title.strip()[:160],
        "summary": summary.strip()[:4000],
        "steps": normalized,
        "requires_approval": True,
        "actions_executed": False,
    }
