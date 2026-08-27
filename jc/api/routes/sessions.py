"""Session management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from jc.database.session import get_db
from jc.database.models import SessionModel, MessageModel

router = APIRouter()


class SessionCreate(BaseModel):
    user_id: str
    metadata: dict = {}


class MessageCreate(BaseModel):
    role: str  # user, assistant, system
    content: str
    metadata: dict = {}


class SessionResponse(BaseModel):
    id: str
    user_id: str
    conversation_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    context: dict

    class Config:
        from_attributes = True


@router.post("/")
async def create_session(session_req: SessionCreate, db: Session = Depends(get_db)):
    """Create new conversation session"""
    conversation_id = f"conv-{uuid4()}"
    
    session = SessionModel(
        user_id=session_req.user_id,
        conversation_id=conversation_id,
        status="active",
        context=session_req.metadata,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id": session.id,
        "conversation_id": session.conversation_id,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session details"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "conversation_id": session.conversation_id,
        "user_id": session.user_id,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "context": session.context,
    }


@router.post("/{session_id}/messages")
async def add_message(
    session_id: str, message: MessageCreate, db: Session = Depends(get_db)
):
    """Add message to session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    msg = MessageModel(
        session_id=session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata,
    )
    db.add(msg)
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)
    
    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }


@router.get("/{session_id}/messages")
async def get_messages(session_id: str, db: Session = Depends(get_db)):
    """Get all messages in session"""
    messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).all()
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


@router.put("/{session_id}")
async def update_session(
    session_id: str, updates: dict, db: Session = Depends(get_db)
):
    """Update session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "status" in updates:
        session.status = updates["status"]
    if "context" in updates:
        session.context = updates["context"]
    
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {"id": session.id, "status": session.status, "updated_at": session.updated_at.isoformat()}


@router.delete("/{session_id}")
async def end_session(session_id: str, db: Session = Depends(get_db)):
    """End conversation session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "ended"
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {"id": session.id, "status": "ended", "ended_at": datetime.utcnow().isoformat()}
