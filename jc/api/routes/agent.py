"""Supervised agent planning endpoint. Plans are saved, never auto-executed."""
from time import perf_counter

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from jc.config.environment import settings
from jc.core.agent_planner import build_planning_prompt, parse_plan_response
from jc.core.ai_provider import generate_response
from jc.database.models import SessionModel, TaskModel
from jc.database.session import get_db

router = APIRouter()


class PlanRequest(BaseModel):
    session_id: str = Field(min_length=1)
    goal: str = Field(min_length=3, max_length=12000)
    language: str = Field(default="English", max_length=40)
    model: str | None = None


@router.post("/plan")
async def plan_task(request: PlanRequest, db: Session = Depends(get_db)):
    """Ask the configured model to decompose a goal and persist an approval-gated plan."""
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    model = request.model or settings.DEFAULT_MODEL
    prompt = build_planning_prompt(request.goal, request.language)
    started = perf_counter()
    try:
        raw, tokens_used = generate_response(
            prompt,
            model,
            settings.AGENT_TEMPERATURE,
            min(settings.AGENT_MAX_TOKENS, 4000),
            config=settings,
        )
        plan = parse_plan_response(raw)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="The AI planner returned an invalid plan. Please retry.") from exc
    except RuntimeError as exc:
        message = str(exc)
        status = 503 if "API key is not configured" in message else 502
        detail = message if status == 503 else "The AI provider did not return a usable plan."
        raise HTTPException(status_code=status, detail=detail) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Could not reach the configured AI provider.") from exc

    task = TaskModel(
        session_id=session.id,
        user_id=session.user_id,
        title=plan["title"],
        description=plan["summary"],
        status="pending_approval",
        priority="normal",
        plan=plan,
        subtasks=plan["steps"],
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "title": task.title,
        "summary": task.description,
        "status": task.status,
        "plan": plan,
        "tokens_used": tokens_used,
        "latency_ms": round((perf_counter() - started) * 1000),
        "requires_approval": True,
        "actions_executed": False,
        "message": "Plan saved. No external actions have been performed. Review and approve steps before execution.",
    }
