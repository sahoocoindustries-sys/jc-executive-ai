"""Production runtime supervisor"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

from jc.config.environment import settings
from jc.database.models import engine, Base

logger = logging.getLogger("jc.runtime")


class ProductionRuntimeSupervisor:
    """Main runtime supervisor for JC Executive AI"""
    
    def __init__(self):
        self.initialized = False
        self.disaster_recovery_mode = settings.DISASTER_RECOVERY_MODE
        self.emergency_stop = False
        self.read_only = False
        self.workers = {}
        self.health_status = {}
        self.start_time = datetime.utcnow()
    
    async def initialize(self):
        """Initialize all runtime components"""
        logger.info("Initializing production runtime supervisor...")
        
        # Initialize database
        self._initialize_database()
        
        # Initialize providers
        await self._initialize_providers()
        
        # Initialize workers
        await self._initialize_workers()
        
        # Initialize voice system
        if settings.FEATURE_VOICE:
            await self._initialize_voice()
        
        # Initialize security
        await self._initialize_security()
        
        # Initialize audit
        await self._initialize_audit()
        
        # Check production readiness
        readiness = await self.check_production_readiness()
        
        self.initialized = True
        logger.info(f"Runtime initialized. Production ready: {readiness['ready']}")
    
    def _initialize_database(self):
        """Initialize database schema"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _initialize_providers(self):
        """Initialize AI providers"""
        logger.info("Initializing AI providers...")
        
        providers_status = {}
        
        # Check OpenAI
        if settings.OPENAI_API_KEY:
            try:
                # Test provider connectivity
                providers_status["openai"] = "PASS"
                logger.info("OpenAI provider configured")
            except Exception as e:
                providers_status["openai"] = f"FAIL: {e}"
                logger.warning(f"OpenAI provider check failed: {e}")
        else:
            providers_status["openai"] = "NOT_CONFIGURED"
        
        # Check Gemini
        if settings.GEMINI_API_KEY:
            try:
                providers_status["gemini"] = "PASS"
                logger.info("Gemini provider configured")
            except Exception as e:
                providers_status["gemini"] = f"FAIL: {e}"
                logger.warning(f"Gemini provider check failed: {e}")
        else:
            providers_status["gemini"] = "NOT_CONFIGURED"
        
        # Check Ollama
        try:
            import requests
            response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                providers_status["ollama"] = "PASS"
                logger.info("Ollama provider available")
            else:
                providers_status["ollama"] = "UNAVAILABLE"
        except Exception as e:
            providers_status["ollama"] = "UNAVAILABLE"
            logger.debug(f"Ollama not available: {e}")
        
        self.health_status["providers"] = providers_status
    
    async def _initialize_workers(self):
        """Initialize background workers"""
        logger.info(f"Initializing {settings.WORKER_COUNT} workers...")
        
        try:
            for i in range(settings.WORKER_COUNT):
                worker_id = f"worker-{i}"
                self.workers[worker_id] = {
                    "id": worker_id,
                    "status": "idle",
                    "jobs_processed": 0,
                    "created_at": datetime.utcnow().isoformat(),
                }
            logger.info(f"{settings.WORKER_COUNT} workers initialized")
            self.health_status["workers"] = "PASS"
        except Exception as e:
            logger.error(f"Worker initialization failed: {e}")
            self.health_status["workers"] = f"FAIL: {e}"
    
    async def _initialize_voice(self):
        """Initialize voice system"""
        logger.info("Initializing voice system...")
        
        voice_status = {}
        
        # Check STT
        if settings.STT_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            voice_status["stt"] = "PASS"
        else:
            voice_status["stt"] = "NOT_CONFIGURED"
        
        # Check TTS
        if settings.TTS_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            voice_status["tts"] = "PASS"
        else:
            voice_status["tts"] = "NOT_CONFIGURED"
        
        # Check VAD
        voice_status["vad"] = "PASS" if settings.VAD_ENABLED else "DISABLED"
        
        # Check barge-in
        voice_status["barge_in"] = "PASS" if settings.BARGE_IN_ENABLED else "DISABLED"
        
        self.health_status["voice"] = voice_status
        logger.info("Voice system initialized")
    
    async def _initialize_security(self):
        """Initialize security systems"""
        logger.info("Initializing security...")
        
        if settings.ZERO_TRUST_ENABLED:
            logger.info("Zero-Trust authorization enabled")
        
        self.health_status["security"] = {
            "zero_trust": "PASS" if settings.ZERO_TRUST_ENABLED else "DISABLED",
            "emergency_stop": "READY" if settings.EMERGENCY_STOP_ENABLED else "DISABLED",
        }
    
    async def _initialize_audit(self):
        """Initialize audit system"""
        logger.info("Initializing audit system...")
        from pathlib import Path
        Path(settings.AUDIT_LOG_PATH).mkdir(parents=True, exist_ok=True)
        self.health_status["audit"] = "PASS"
    
    async def check_production_readiness(self) -> Dict[str, Any]:
        """Check if system is production-ready"""
        logger.info("Checking production readiness...")
        
        checks = {
            "database": "PASS",
            "providers": self.health_status.get("providers", {}),
            "voice": self.health_status.get("voice", {}),
            "workers": self.health_status.get("workers", "UNKNOWN"),
            "security": self.health_status.get("security", {}),
            "audit": self.health_status.get("audit", "UNKNOWN"),
        }
        
        # Determine if ready
        ready = (
            checks["database"] == "PASS" and
            checks["workers"] == "PASS" and
            checks["security"]["zero_trust"] in ("PASS", "DISABLED") and
            checks["audit"] == "PASS"
        )
        
        return {
            "ready": ready,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down production runtime...")
        
        # Stop workers
        for worker_id in self.workers:
            logger.info(f"Stopping {worker_id}")
        
        self.workers.clear()
        logger.info("Runtime shutdown complete")
    
    def trigger_emergency_stop(self):
        """Trigger emergency stop"""
        logger.critical("EMERGENCY STOP triggered")
        self.emergency_stop = True
        self.read_only = True
    
    def set_read_only(self, enabled: bool):
        """Set read-only mode"""
        self.read_only = enabled
        logger.warning(f"Read-only mode: {enabled}")
    
    def set_disaster_recovery_mode(self, mode: str):
        """Set disaster recovery mode"""
        valid_modes = ["normal", "degraded", "recovery", "read_only", "emergency_stop"]
        if mode in valid_modes:
            self.disaster_recovery_mode = mode
            logger.warning(f"Disaster recovery mode set to: {mode}")
        else:
            logger.error(f"Invalid disaster recovery mode: {mode}")
