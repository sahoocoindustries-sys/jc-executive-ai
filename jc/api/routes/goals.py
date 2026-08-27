"""Goal management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from jc.database.session import get_db
from jc.database.models import GoalModel

router = APIRouter()


class GoalCreate(BaseModel):
    user_id: str
    title: str
    description: str
    target: str
    target_completion: Optional[datetime] = None
    milestones: Optional[List[dict]] = []


class GoalUpdate(BaseModel):
    status: Optional[str] = None
    current_progress: Optional[float] = None


@router.post("/")
async def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """Create strategic goal"""
    db_goal = GoalModel(
        user_id=goal.user_id,
        title=goal.title,
        description=goal.description,
        target=goal.target,
        target_completion=goal.target_completion,
        milestones=goal.milestones,
        status="active",
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return {
        "id": db_goal.id,
        "title": db_goal.title,
        "status": db_goal.status,
        "progress": db_goal.current_progress,
        "created_at": db_goal.created_at.isoformat(),
    }


@router.get("/{goal_id}")
async def get_goal(goal_id: str, db: Session = Depends(get_db)):
    """Get goal details"""
    goal = db.query(GoalModel).filter(GoalModel.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return {
        "id": goal.id,
        "title": goal.title,
        "description": goal.description,
        "status": goal.status,
        "target": goal.target,
        "progress": goal.current_progress,
        "milestones": goal.milestones,
        "dependencies": goal.dependencies,
        "risk_factors": goal.risk_factors,
        "created_at": goal.created_at.isoformat(),
        "target_completion": goal.target_completion.isoformat() if goal.target_completion else None,
    }


@router.put("/{goal_id}")
async def update_goal(goal_id: str, update: GoalUpdate, db: Session = Depends(get_db)):
    """Update goal progress"""
    goal = db.query(GoalModel).filter(GoalModel.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if update.status:
        goal.status = update.status
    if update.current_progress is not None:
        goal.current_progress = update.current_progress
    
    db.commit()
    
    return {
        "id": goal.id,
        "status": goal.status,
        "progress": goal.current_progress,
    }


@router.get("/user/{user_id}")
async def list_user_goals(user_id: str, db: Session = Depends(get_db)):
    """List all goals for user"""
    goals = db.query(GoalModel).filter(GoalModel.user_id == user_id).all()
    return [
        {
            "id": goal.id,
            "title": goal.title,
            "status": goal.status,
            "progress": goal.current_progress,
        }
        for goal in goals
    ]
