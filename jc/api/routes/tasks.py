"""Task and workflow management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from uuid import uuid4
from jc.database.session import get_db
from jc.database.models import TaskModel

router = APIRouter()


class TaskCreate(BaseModel):
    session_id: str
    user_id: str
    title: str
    description: str
    priority: Optional[str] = "normal"
    plan: Optional[dict] = {}
    subtasks: Optional[List[dict]] = []


class TaskUpdate(BaseModel):
    status: Optional[Literal["pending", "pending_approval", "cancelled"]] = None
    priority: Optional[str] = None
    result: Optional[dict] = None


@router.post("/")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create new task/workflow"""
    db_task = TaskModel(
        session_id=task.session_id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        plan=task.plan,
        subtasks=task.subtasks,
        status="pending",
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return {
        "id": db_task.id,
        "title": db_task.title,
        "status": db_task.status,
        "priority": db_task.priority,
        "created_at": db_task.created_at.isoformat(),
    }


@router.get("/{task_id}")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get task details"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "plan": task.plan,
        "subtasks": task.subtasks,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@router.put("/{task_id}")
async def update_task(task_id: str, update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task status and details"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if update.status:
        task.status = update.status
        if update.status == "executing":
            task.started_at = datetime.utcnow()
        elif update.status == "completed":
            task.completed_at = datetime.utcnow()
    
    if update.priority:
        task.priority = update.priority
    
    if update.result:
        task.result = update.result
    
    db.commit()
    
    return {
        "id": task.id,
        "status": task.status,
        "priority": task.priority,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.post("/{task_id}/execute")
async def execute_task(task_id: str, db: Session = Depends(get_db)):
    """Execute task with plan"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    raise HTTPException(
        status_code=501,
        detail="Task execution is not implemented yet. The task remains saved and no external action was performed.",
    )


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """Cancel task execution"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "cancelled"
    db.commit()
    
    return {
        "id": task.id,
        "status": "cancelled",
        "cancelled_at": datetime.utcnow().isoformat(),
    }
