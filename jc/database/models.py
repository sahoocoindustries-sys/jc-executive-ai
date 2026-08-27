"""Database models and initialization"""
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Integer, Float, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from uuid import uuid4

from jc.config.environment import settings

# Database setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
Base = declarative_base()


class SessionModel(Base):
    """Conversation session"""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    conversation_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active, paused, ended
    context = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    messages = relationship("MessageModel", back_populates="session")
    tasks = relationship("TaskModel", back_populates="session")


class MessageModel(Base):
    """Conversation message"""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON, default=dict)
    token_count = Column(Integer, default=0)

    session = relationship("SessionModel", back_populates="messages")


class MemoryModel(Base):
    """Long-term semantic memory"""
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, index=True)
    content = Column(Text)
    embedding = Column(JSON)  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confidence = Column(Float, default=1.0)
    tags = Column(JSON, default=list)
    relationships = Column(JSON, default=list)


class TaskModel(Base):
    """Task/workflow execution"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="pending")  # pending, executing, completed, failed
    priority = Column(String, default="normal")  # low, normal, high, critical
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    plan = Column(JSON, default=dict)
    subtasks = Column(JSON, default=list)
    result = Column(JSON)
    error = Column(Text)

    session = relationship("SessionModel", back_populates="tasks")


class GoalModel(Base):
    """Strategic goals and objectives"""
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="active")  # active, paused, completed, failed
    target = Column(String)  # Measurable target
    current_progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    target_completion = Column(DateTime)
    milestones = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    risk_factors = Column(JSON, default=list)


class DecisionModel(Base):
    """Decision records with evidence and outcomes"""
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    candidates = Column(JSON, default=list)  # Option candidates
    evidence = Column(JSON, default=list)
    constraints = Column(JSON, default=list)
    decision = Column(String)  # Final decision
    confidence = Column(Float, default=0.5)
    risk_assessment = Column(JSON, default=dict)
    approval_status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime)
    outcome = Column(JSON)
    explanation = Column(Text)


class AuditLogModel(Base):
    """Immutable audit trail"""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actor = Column(String, index=True)  # User/system actor
    action = Column(String, index=True)  # Action type
    resource = Column(String, index=True)  # Resource affected
    details = Column(JSON, default=dict)
    result = Column(String)  # success, failure, denied
    session_id = Column(String, index=True)
    task_id = Column(String, index=True)
    correlation_id = Column(String, index=True)
    severity = Column(String)  # info, warning, error, critical
    policy_result = Column(JSON, default=dict)
    hash = Column(String)  # For integrity verification


class BackupModel(Base):
    """Database backup metadata"""
    __tablename__ = "backups"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    path = Column(String, unique=True)
    size = Column(Integer)  # Bytes
    checksum = Column(String)  # SHA-256 hash
    status = Column(String, default="valid")  # valid, invalid, corrupted
    restore_tested = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)


class HealthCheckModel(Base):
    """System health and metrics"""
    __tablename__ = "health_checks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    component = Column(String, index=True)
    status = Column(String)  # healthy, degraded, unhealthy
    latency_ms = Column(Integer)
    error_rate = Column(Float)
    details = Column(JSON, default=dict)
