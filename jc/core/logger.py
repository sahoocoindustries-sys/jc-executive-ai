"""Core logging setup"""
import logging
import json
from datetime import datetime
from pathlib import Path


def setup_logging(level: str = "INFO"):
    """Configure structured logging"""
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Create logs directory
    Path("./logs").mkdir(exist_ok=True)
    Path("./logs/audit").mkdir(exist_ok=True)
    
    return logging.getLogger("jc")


class AuditLogger:
    """Structured audit logging with integrity"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger("jc.audit")
    
    def log_event(
        self,
        actor: str,
        action: str,
        resource: str,
        result: str,
        details: dict = None,
        severity: str = "info",
        correlation_id: str = None,
    ):
        """Log audit event with structured data"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
            "severity": severity,
            "correlation_id": correlation_id,
            "details": details or {},
        }
        
        self.logger.info(json.dumps(event))
        
        # Store in database if available
        if self.db_session:
            from jc.database.models import AuditLogModel
            audit_record = AuditLogModel(
                actor=actor,
                action=action,
                resource=resource,
                result=result,
                details=details or {},
                severity=severity,
                correlation_id=correlation_id,
            )
            self.db_session.add(audit_record)
            self.db_session.commit()
