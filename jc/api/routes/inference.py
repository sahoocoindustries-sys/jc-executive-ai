"""AI inference endpoints backed by real configured model providers."""
from datetime import datetime
from time import perf_counter
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from jc.config.environment import settings
from jc.core.ai_provider import generate_response
from jc.database.models import MessageModel, SessionModel
from jc.database.session import get_db

router = APIRouter()


class InferenceRequest(BaseModel):
    session_id: str
    prompt: str = Field(min_length=1, max_length=30000)
    model: Optional[str] = "gemini-2.5-flash"
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=2000, ge=1, le=8192)
    stream: Optional[bool] = False


class InferenceResponse(BaseModel):
    id: str
    session_id: str
    response: str
    tokens_used: int
    cost: float
    latency_ms: int
    model: str
    timestamp: datetime


@router.post("/")
async def inference(req: InferenceRequest, db: Session = Depends(get_db)):
    """Run real inference; never store a fabricated assistant response."""
    session = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt must not be blank")

    model = req.model or settings.DEFAULT_MODEL
    started = perf_counter()
    try:
        response_text, tokens_used = generate_response(
            prompt,
            model,
            req.temperature if req.temperature is not None else settings.AGENT_TEMPERATURE,
            req.max_tokens if req.max_tokens is not None else settings.AGENT_MAX_TOKENS,
            config=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        message = str(exc)
        status_code = 503 if "API key is not configured" in message else 502
        safe_message = message if status_code == 503 else "The AI provider did not return a usable response."
        raise HTTPException(status_code=status_code, detail=safe_message) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not reach the configured AI provider. Check connectivity and provider configuration.",
        ) from exc

    elapsed_ms = round((perf_counter() - started) * 1000)
    user_msg = MessageModel(session_id=req.session_id, role="user", content=prompt)
    assistant_msg = MessageModel(
        session_id=req.session_id,
        role="assistant",
        content=response_text,
        token_count=tokens_used,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_msg)

    return {
        "id": assistant_msg.id,
        "session_id": req.session_id,
        "response": response_text,
        "tokens_used": tokens_used,
        # Exact provider pricing varies by model/account and is not configured here.
        "cost": 0.0,
        "latency_ms": elapsed_ms,
        "model": model,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/stream")
async def streaming_inference(req: InferenceRequest, db: Session = Depends(get_db)):
    """Streaming is not implemented yet; do not claim it has started."""
    session = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    raise HTTPException(
        status_code=501,
        detail="Streaming inference is not implemented yet. Use POST /api/inference/ for a complete response.",
    )


@router.post("/tool-call")
async def tool_call(req: dict, db: Session = Depends(get_db)):
    """Tool execution is not enabled until a governed tool registry is connected."""
    session_id = req.get("session_id")
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    raise HTTPException(
        status_code=501,
        detail="Tool execution is not implemented yet; no external action was performed.",
    )
