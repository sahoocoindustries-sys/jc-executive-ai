"""Decision intelligence endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from jc.database.session import get_db
from jc.database.models import DecisionModel

router = APIRouter()


class DecisionCreate(BaseModel):
    user_id: str
    title: str
    description: str
    candidates: List[str]
    constraints: Optional[List[str]] = []
    evidence: Optional[List[dict]] = []


class DecisionMake(BaseModel):
    decision: str
    confidence: float
    explanation: str
    risk_assessment: Optional[dict] = {}


@router.post("/")
async def create_decision(
    decision: DecisionCreate, db: Session = Depends(get_db)
):
    """Create decision record"""
    db_decision = DecisionModel(
        user_id=decision.user_id,
        title=decision.title,
        description=decision.description,
        candidates=decision.candidates,
        constraints=decision.constraints,
        evidence=decision.evidence,
        approval_status="pending",
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)
    
    return {
        "id": db_decision.id,
        "title": db_decision.title,
        "approval_status": db_decision.approval_status,
        "candidates": db_decision.candidates,
        "created_at": db_decision.created_at.isoformat(),
    }


@router.post("/{decision_id}/decide")
async def make_decision(
    decision_id: str,
    decision_data: DecisionMake,
    db: Session = Depends(get_db),
):
    """Make decision with governance"""
    decision = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision.decision = decision_data.decision
    decision.confidence = decision_data.confidence
    decision.explanation = decision_data.explanation
    decision.risk_assessment = decision_data.risk_assessment
    decision.decided_at = datetime.utcnow()
    decision.approval_status = "approved"
    
    db.commit()
    
    return {
        "id": decision.id,
        "decision": decision.decision,
        "confidence": decision.confidence,
        "approval_status": decision.approval_status,
        "decided_at": decision.decided_at.isoformat(),
    }


@router.get("/{decision_id}")
async def get_decision(decision_id: str, db: Session = Depends(get_db)):
    """Get decision details"""
    decision = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return {
        "id": decision.id,
        "title": decision.title,
        "candidates": decision.candidates,
        "decision": decision.decision,
        "confidence": decision.confidence,
        "explanation": decision.explanation,
        "approval_status": decision.approval_status,
        "risk_assessment": decision.risk_assessment,
        "created_at": decision.created_at.isoformat(),
        "decided_at": decision.decided_at.isoformat() if decision.decided_at else None,
    }
