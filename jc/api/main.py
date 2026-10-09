"""JC Executive AI - Main application entry point"""
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from jc.config.environment import settings
from jc.database.models import Base, engine
from jc.database.session import SessionLocal
from jc.core.logger import setup_logging
from jc.core.runtime import ProductionRuntimeSupervisor

# Setup logging
logger = setup_logging(settings.LOG_LEVEL)

# Initialize database
Base.metadata.create_all(bind=engine)

# Create FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="JC Executive AI",
    description="Production-Grade Personal AI Operating System",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global runtime supervisor
runtime_supervisor: ProductionRuntimeSupervisor | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize runtime on startup"""
    global runtime_supervisor
    logger.info("JC Executive AI starting up...")
    
    try:
        runtime_supervisor = ProductionRuntimeSupervisor()
        await runtime_supervisor.initialize()
        logger.info("Runtime supervisor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize runtime: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global runtime_supervisor
    logger.info("JC Executive AI shutting down...")
    
    if runtime_supervisor:
        await runtime_supervisor.shutdown()
    logger.info("Shutdown complete")


if (project_root / "web").is_dir():
    app.mount("/web", StaticFiles(directory=project_root / "web", html=True), name="web")


# Import and include routers
from jc.api.routes import (
    health,
    sessions,
    inference,
    voice,
    tasks,
    goals,
    decisions,
    autonomy,
    production,
    audit,
    agent,
)

app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(inference.router, prefix="/api/inference", tags=["Inference"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(autonomy.router, prefix="/api/autonomy", tags=["Autonomy"])
app.include_router(production.router, prefix="/api/production", tags=["Production"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "JC Executive AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "sessions": "/api/sessions",
            "inference": "/api/inference",
            "voice": "/api/voice",
            "tasks": "/api/tasks",
            "goals": "/api/goals",
            "decisions": "/api/decisions",
            "autonomy": "/api/autonomy",
            "production": "/api/production",
            "audit": "/api/audit",
            "agent_planning": "/api/agent/plan",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
